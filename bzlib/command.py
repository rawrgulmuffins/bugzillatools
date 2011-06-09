# This file is part of bugzillatools
# Copyright (C) 2011 Benon Technologies Pty Ltd
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

from . import config


def arg(*args, **kwargs):
    """Convenience function to create argparse arguments."""
    return {'args': args, 'kwargs': kwargs}


class Command(object):
    """A command object.

    Provides arguments.  Does what it does using __call__.
    """

    """
    An array of (args, kwargs) tuples that will be used as arguments to
    ArgumentParser.add_argument().
    """
    args = []

    def __init__(self, bugzilla):
        """Initialise the Command object."""
        self.bz = bugzilla

    def __call__(self, *args, **kwargs):
        """To be implemented by subclasses."""
        raise NotImplementedError


class Assign(Command):
    """Reassign the given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
        arg('--to', metavar='ASSIGNEE', help='New assignee'),
        arg('-m', '--message', help='Comment on the change'),
    ]

    def __call__(self, args):
        return map(
            lambda x: self.bz.bug(x).set_assigned_to(
                args.to,
                comment=args.message
            ),
            args.bugs
        )


class Comment(Command):
    """Comment on the given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
        arg('-m', '--message', help='Comment on the change'),
    ]

    def __call__(self, args):
        map(lambda x: self.bz.bug(x).add_comment(args.message), args.bugs)


class Fix(Command):
    """Fix the given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
        arg('-m', '--message', help='Comment on the change'),
    ]

    def __call__(self, args):
        return map(
            lambda x: self.bz.bug(x).set_status(
                'RESOLVED',
                resolution='FIXED',
                comment=args.message
            ),
            args.bugs
        )


class Info(Command):
    """Show detailed information about the given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
    ]

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


class List(Command):
    """Show a one-line summary of given given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
    ]

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


class Reop(Command):
    """Reopen the given bugs."""
    args = [
        arg('bugs', metavar='BUG', type=int, nargs='+', help='Bug number'),
        arg('-m', '--message', help='Comment on the change'),
    ]

    def __call__(self, args):
        return map(
            lambda x: self.bz.bug(x).set_status(
                'REOPENED',
                comment=args.message
            ),
            args.bugs
        )


class Search(Command):
    pass


commands = [
    Assign,
    Comment,
    Fix,
    Info,
    List,
    Reop,
]
