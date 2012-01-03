# This file is part of bugzillatools
# Copyright (C) 2011, 2012 Fraser Tweedale, Benon Technologies Pty Ltd
#
# bugzillatools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import functools
import math
import re
import sys

from . import bugzilla as _bugzilla

curry = functools.partial


class InvalidInputError(Exception):
    pass


class RejectWarning(Warning):
    pass


def number(items):
    """Maps numbering onto given values"""
    n = len(items)
    width = math.log10(n - 1) // 1 + 1 if n > 1 else 1
    return map(
        lambda x: '[{0[0]:{1}}] {0[1]}'.format(x, int(width)),
        enumerate(items)
    )


def filter_yn(string, default=None):
    """Return True if yes, False if no, or the default."""
    if string.startswith(('Y', 'y')):
        return True
    elif string.startswith(('N', 'n')):
        return False
    elif not string and default is not None:
        return True if default else False
    raise InvalidInputError


def filter_int(string, default=None, start=None, stop=None):
    """Return the input integer, or the default."""
    try:
        i = int(string)
        if start is not None and i < start:
            raise InvalidInputError(
                'value too small; minimum is {}'.format(start))
        if stop is not None and i >= stop:
            raise InvalidInputError(
                'value too large; maximum is {}'.format(stop - 1))
        return i
    except ValueError:
        if not string and default is not None:
            # empty string, default was given
            return default
        else:
            raise InvalidInputError('not an int: {!r}'.format(string))


def filter_list(
    string,
    default=None,
    filter=None,
    min_allowed=None,
    max_allowed=None,
    allow_duplicates=True,
    filter_duplicates=True
):
    """Return a list of values, or the default list.

    string
      A string of values delimited by commas, colons, semicolons and
      whitespace.
    default
      A list of values (possibly empty), or None.
    min_allowed
      The minimum number of responses allowed (inclusive), or None.
    max_allowed
      The maximum number of responses allowed (exclusive), or None.
    allow_duplicates
      Whether duplicates are allowed in the input.  Defaults to True.
    filter_duplicates
      Whether duplicates are filtered out of the list before returning.
      Defaults to True.

    The min_allowed and max_allowed constraints are applied after
    duplicates are filtered out, if the duplicate filtering behaviour
    is used.
    """
    if filter is None:
        raise TypeError("argument 'filter' not given")
    if not string and default is not None:
        return default
    strs = re.split(r'[\s:;,]+', string)
    strs = strs[1:] if strs and not strs[0] else strs
    strs = strs[:-1] if strs and not strs[-1] else strs
    values = [filter(s) for s in strs]
    valueset = set(values)
    if len(valueset) != len(values):
        if not allow_duplicates:
            raise InvalidInputError('duplicate values are not allowed')
        if filter_duplicates:
            values = list(valueset)
    if min_allowed is not None and len(values) < min_allowed:
        raise InvalidInputError('too few values supplied')
    if max_allowed is not None and len(values) > max_allowed:
        raise InvalidInputError('too many values supplied')
    return values


def filter_decimal(string, default=None, lower=None, upper=None):
    """Return the input decimal number, or the default."""
    try:
        d = decimal.Decimal(string)
        if lower is not None and d < lower:
            raise InvalidInputError("value too small")
        if upper is not None and d >= upper:
            raise InvalidInputError("value too large")
        return d
    except decimal.InvalidOperation:
        if not string and default is not None:
            # empty string, default was given
            return default
        else:
            raise InvalidInputError("invalid decimal number")


def filter_text(string, default=None):
    if string:
        return string
    elif default is not None:
        return default
    else:
        raise InvalidInputError


def filter_user(string, bugzilla=None, default=None):
    """Match to a single user and return the user name.

    ``bugzilla``
      A ``bzlib.bugzilla.Bugzilla``.
    """
    if not string and default:
        return None
    try:
        return bugzilla.match_one_user(string)['name']
    except _bugzilla.UserError as e:
        raise InvalidInputError(e.message)


class UI(object):
    def show(self, msg):
        print msg

    def bail(self, msg=None):
        """Exit uncleanly with an optional message"""
        if msg:
            self.show('BAIL OUT: ' + msg)
        sys.exit(1)

    def input(self, filter_fn, prompt):
        """Prompt user until valid input is received.

        RejectWarning is raised if a KeyboardInterrupt is caught.
        """
        while True:
            try:
                return filter_fn(raw_input(prompt))
            except InvalidInputError as e:
                if e.message:
                    self.show('ERROR: ' + e.message)
            except EOFError:
                raise RejectWarning
            except KeyboardInterrupt:
                raise RejectWarning

    def text(self, prompt, default=None):
        """Prompts the user for some text, with optional default"""
        prompt = prompt if prompt is not None else 'Enter some text'
        prompt += " [{0}]: ".format(default) if default is not None else ': '
        return self.input(curry(filter_text, default=default), prompt)

    def user(self, prompt, bugzilla=None, default=None):
        """Prompt the user for a username on the given ``Bugzilla``."""
        prompt = prompt if prompt is not None else 'Enter a user name'
        prompt += " [{}]: ".format(default) if default is not None else ': '
        return self.input(
            curry(filter_user, bugzilla=bugzilla, default=default), prompt)

    def user_list(self, prompt, bugzilla=None, default=None):
        """Prompt the user for a list of usernames on the ``Bugzilla``."""
        prompt = prompt if prompt is not None else 'Enter a user name'
        prompt += " [{}]: ".format(default) if default is not None else ': '
        return self.input(
            curry(
                filter_list,
                default=default,
                filter=curry(filter_user, bugzilla=bugzilla)
            ),
            prompt
        )

    def bugno(self, prompt, default=None):
        prompt = prompt if prompt is None else 'Enter an bug number'
        prompt += " [{0}]: ".format(default) if default is not None else ': '
        return self.input(curry(filter_int, start=1, default=default), prompt)

    def decimal(self, prompt, default=None, lower=None, upper=None):
        """Prompts user to input decimal, with optional default and bounds."""
        prompt = prompt if prompt is not None else "Enter a decimal number"
        prompt += " [{0}]: ".format(default) if default is not None else ': '
        return self.input(
            curry(filter_decimal, default=default, lower=lower, upper=upper),
            prompt
        )

    def yn(self, prompt, default=None):
        """Prompts the user for yes/no confirmation, with optional default"""
        if default is True:
            opts = " [Y/n]: "
        elif default is False:
            opts = " [y/N]: "
        else:
            opts = " [y/n]: "
        prompt += opts
        return self.input(curry(filter_yn, default=default), prompt)

    def choose(self, prompt, items, default=None):
        """Prompts the user to choose one item from a list.

        The default, if provided, is an index; the item of that index will
        be returned.

        If the list has a single item, that item is returned without
        prompting the user at all.
        """
        if len(items) == 1:
            return items[0]  # only one item; return it without prompting
        if default is not None and (default >= len(items) or default < 0):
            raise IndexError
        prompt = prompt if prompt is not None else "Choose from following:"
        self.show(prompt + '\n')
        self.show("\n".join(number(items)))  # show the items
        prompt = "Enter number of chosen item"
        prompt += " [{0}]: ".format(default) if default is not None else ': '
        return items[self.input(
            curry(filter_int, default=default, start=0, stop=len(items)),
            prompt
        )]

    def chooseN(self,
        prompt,
        items,
        default=None,
        min_allowed=None,
        max_allowed=None
    ):
        """Prompt the user to choose multiple items from a list.

        prompt:
            Message with which to prompt user.  If None given, a default
            prompt is generated.
        items:
            A list of items from which to choose.
        default:
            A list of indices.  If the default is used, the list of values
            corresponding to these indices will be returned.  If any value
            is out of range, IndexError is raised.
        min_allowed:
            The minimum number of items that must be chosen from the list
            (inclusive).  Defaults to None (no minimum).
        max_allowed:
            The maximum number of items that must be chosen from the list
            (exclusive).  Defaults to None (no maximum).
        """
        if default and filter(lambda x: x >= len(items) or x < 0, default):
            raise IndexError('Default value ({}) out of range({})'.format(
                default, len(default)
            ))

        prompt = prompt if prompt is not None else \
            "Choose from the following (multiple values may be chosen):"
        self.show(prompt + '\n')
        self.show('\n'.join(number(items)))  # show the items
        prompt = "Enter the numbers of chosen items " \
            "(comma or space separated list)"
        prompt += ' [{}]: '.format(' '.join(default)) if default is not None \
            else ': '
        indices = self.input(
            curry(
                filter_list,
                default=default,
                filter=curry(filter_int, start=0, stop=len(items)),
                min_allowed=min_allowed,
                max_allowed=max_allowed
            ),
            prompt
        )
        return map(lambda x: items[x], indices)
