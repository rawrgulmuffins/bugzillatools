# This file is part of bugzillatools
# Copyright (C) 2011 Fraser Tweedale
#
# ledgertools is free software: you can redistribute it and/or modify
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
import sys

curry = functools.partial


class InvalidInputError(Exception):
    pass


class RejectWarning(Warning):
    pass


def number(items):
    """Maps numbering onto given values"""
    n = len(items)
    if n == 0:
        return items
    places = str(int(math.log10(n) // 1 + 1))
    format = '[{0[0]:' + str(int(places)) + 'd}] {0[1]}'
    return map(
        lambda x: format.format(x),
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
            raise InvalidInputError("value too small")
        if stop is not None and i >= stop:
            raise InvalidInputError("value too large")
        return i
    except ValueError:
        if not string and default is not None:
            # empty string, default was given
            return default
        else:
            raise InvalidInputError


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
            except KeyboardInterrupt:
                raise RejectWarning

    def text(self, prompt, default=None):
        """Prompts the user for some text, with optional default"""
        prompt = prompt if prompt is not None else 'Enter some text'
        prompt += " [{0}]: ".format(default) if default is not None else ': '
        return self.input(curry(filter_text, default=default), prompt)

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
        """
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
