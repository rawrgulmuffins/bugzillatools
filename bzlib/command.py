# This file is part of bugzillatools
# Copyright (C) 2011 Benon Technologies Pty Ltd, Fraser Tweedale
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

import argparse
import itertools

from . import config
from . import editor


def arg(*args, **kwargs):
    """Convenience function to create argparse arguments."""
    return {'args': args, 'kwargs': kwargs}


def with_bugs(cls):
    cls.args = cls.args + [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
    ]
    return cls


def _message_arg_callback(args):
    if not args.message:
        if args.file:
            args.message = args.file.read()
        else:
            args.message = editor.input('Enter your comment.')


def with_message(cls):
    cls.args = cls.args + [
        arg('-F', '--file', metavar='MSGFILE', type=argparse.FileType('r'),
            help='Take comment from this file'),
        arg('-m', '--message', help='Comment on the change'),
    ]
    cls.arg_callbacks.append(_message_arg_callback)
    return cls


class Command(object):
    """A command object.

    Provides arguments.  Does what it does using __call__.
    """

    """
    An array of (args, kwargs) tuples that will be used as arguments to
    ArgumentParser.add_argument().
    """
    args = []
    arg_callbacks = []

    def __init__(self, bugzilla):
        """Initialise the Command object."""
        self.bz = bugzilla

    def __call__(self, *args, **kwargs):
        """To be implemented by subclasses."""
        raise NotImplementedError

    @classmethod
    def _run_arg_callbacks(cls):
        map(lambda x: x(args), cls.arg_callbacks)


@with_bugs
@with_message
class Assign(Command):
    """Assign bugs to the given user."""
    args = [
        arg('--to', metavar='ASSIGNEE', help='New assignee'),
    ]

    def __call__(self, args):
        self.run
        return map(
            lambda x: self.bz.bug(x).set_assigned_to(
                args.to,
                comment=args.message
            ),
            args.bugs
        )


@with_bugs
@with_message
class Comment(Command):
    """Add a comment to the given bugs."""
    def __call__(self, args):
        map(lambda x: self.bz.bug(x).add_comment(args.message), args.bugs)


class Fields(Command):
    """List valid values for bug fields."""
    def __call__(self, args):
        fields = filter(lambda x: 'values' in x, self.bz.get_fields())
        for field in fields:
            keyfn = lambda x: x['visibility_values']
            groups = itertools.groupby(
                sorted(field['values'], None, keyfn),
                keyfn
            )
            print field['name'], ':'
            for key, group in groups:
                values = sorted(group, None, lambda x: int(x['sortkey']))
                if key:
                    print '  {}: {}'.format(
                        key,
                        ','.join(map(lambda x: x['name'], values))
                    )
                else:
                    print '  ', ','.join(map(lambda x: x['name'], values))


@with_bugs
@with_message
class Fix(Command):
    """Mark the given bugs fixed."""

    def __call__(self, args):
        return map(
            lambda x: self.bz.bug(x).set_status(
                'RESOLVED',
                resolution='FIXED',
                comment=args.message
            ),
            args.bugs
        )


@with_bugs
class Info(Command):
    """Show detailed information about the given bugs."""
    def __call__(self, args):
        fields = config.get_show_fields()
        for bug in map(self.bz.bug, args.bugs):
            bug.read()
            print 'Bug {}:'.format(bug.bugno)
            fields = config.get_show_fields() & bug.data.viewkeys()
            width = max(map(len, fields)) - min(map(len, fields)) + 2
            for field in fields:
                print '  {:{}} {}'.format(field + ':', width, bug.data[field])
            print


@with_bugs
class List(Command):
    """Show a one-line summary of given given bugs."""
    def __call__(self, args):
        fields = config.get_show_fields()
        lens = map(lambda x: len(str(x)), args.bugs)
        width = max(lens) - min(lens) + 2
        for bug in map(self.bz.bug, args.bugs):
            bug.read()
            print 'Bug {:{}} {}'.format(
                str(bug.bugno) + ':', width, bug.data['summary']
            )


class New(Command):
    """File a new bug."""
    pass


class Products(Command):
    """List the products of a Bugzilla instance."""
    def __call__(self, args):
        ids = self.bz.rpc('Product', 'get_accessible_products')['ids']
        products = self.bz.rpc('Product', 'get', ids=ids)['products']
        width = max(map(lambda x: len(x['name']), products)) + 1
        for product in products:
            print '{:{}} {}'.format(
                product['name'] + ':', width, product['description']
            )


@with_bugs
@with_message
class Reop(Command):
    """Reopen the given bugs."""
    def __call__(self, args):
        return map(
            lambda x: self.bz.bug(x).set_status(
                'REOPENED',
                comment=args.message
            ),
            args.bugs
        )


class Search(Command):
    """Search for bugs with supplied attributes."""
    pass


commands = [
    Assign,
    Comment,
    Fields,
    Fix,
    Info,
    List,
    Products,
    Reop,
]
