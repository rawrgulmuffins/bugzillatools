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


class _ReadFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        setattr(namespace, self.dest, values.read())


def with_add_remove(src, dst, metavar=None, type=None):
    def decorator(cls):
        cls.args = cls.args + [
            lambda x: x.add_argument('--add', metavar=metavar, type=type,
                nargs='+',
                help="Add {} to {}.".format(src, dst)),
            lambda x: x.add_argument('--remove', metavar=metavar, type=type,
                nargs='+',
                help="Remove {} from {}.".format(src, dst)),
        ]
        return cls
    return decorator


def with_set(src, dst, metavar=None, type=None):
    def decorator(cls):
        cls.args = cls.args + [
            lambda x: x.add_argument('--set', metavar=metavar, type=type,
                nargs='+',
                help="Set {} to {}. Ignore --add, --remove.".format(dst, src)),
        ]
        return cls
    return decorator


def with_bugs(cls):
    cls.args = cls.args + [
        lambda x: x.add_argument('bugs', metavar='BUG', type=int, nargs='+',
            help='Bug number'),
    ]
    return cls


def with_message(cls):
    def msgargs(parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-F', '--file', metavar='MSGFILE', dest='message',
            type=argparse.FileType('r'), action=_ReadFileAction,
            help='Take comment from this file')
        group.add_argument('-m', '--message', help='Comment on the change')
    cls.args = cls.args + [msgargs]
    return cls


def with_optional_message(cls):
    def msgargs(parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-F', '--file', metavar='MSGFILE', dest='message',
            type=argparse.FileType('r'), action=_ReadFileAction,
            help='Take comment from this file')
        group.add_argument('-m', '--message', nargs='?', const=True,
            help='Comment on the change. With no argument, invokes an editor.')
    cls.args = cls.args + [msgargs]
    return cls


def with_status(cls):
    cls.args = cls.args + [
        lambda x: x.add_argument('--status',
            help='Specify a resolution (case-insensitive).'),
        lambda x: x.add_argument('--choose-status', action='store_true',
            help='Choose status from a list.')
    ]
    return cls


def with_resolution(cls):
    cls.args = cls.args + [
        lambda x: x.add_argument('--resolution',
            help='Specify a resolution (case-insensitive).'),
        lambda x: x.add_argument('--choose-resolution', action='store_true',
            help='Choose resolution from a list.')
    ]
    return cls


def with_limit(things='items', default=None):
    def decorator(cls):
        cls.args = cls.args + [
            lambda x: x.add_argument('--limit', '-l', type=int,
                default=default, metavar='N',
                help='Limit output to N {}.'.format(things))
        ]
        return cls
    return decorator


class Command(object):
    """A command object.

    Provides arguments.  Does what it does using __call__.
    """

    """
    An array of (args, kwargs) tuples that will be used as arguments to
    ArgumentParser.add_argument().
    """
    args = []

    def __init__(self, bugzilla, ui):
        """Initialise the Command object."""
        self.bz = bugzilla
        self.ui = ui

    def __call__(self, *args, **kwargs):
        """To be implemented by subclasses."""
        raise NotImplementedError


@with_bugs
@with_optional_message
class Assign(Command):
    """Assign bugs to the given user."""
    args = [
        lambda x: x.add_argument('--to', metavar='ASSIGNEE',
            help='New assignee'),
    ]

    def __call__(self, args):
        message = editor.input('Enter your comment.') if args.message is True \
            else args.message
        return map(
            lambda x: self.bz.bug(x).set_assigned_to(args.to, comment=message),
            args.bugs
        )


@with_set('given bugs', 'blocked bugs', metavar='BUG', type=int)
@with_add_remove('given bugs', 'blocked bugs', metavar='BUG', type=int)
@with_bugs
@with_optional_message
class Block(Command):
    """List or update bug dependencies."""
    def __call__(self, args):
        bugs = map(self.bz.bug, args.bugs)
        if args.add or args.remove or args.set:
            message = editor.input('Enter your comment.') \
                if args.message is True else args.message
            # update blocked bugs
            map(
                lambda x: self.bz.bug(x).update_block(
                    add=args.add,
                    remove=args.remove,
                    set=args.set,
                    comment=message
                ),
                args.bugs
            )
        else:
            # show blocked bugs
            for bug in bugs:
                bug.read()
                print 'Bug {}:'.format(bug.bugno)
                if bug.data['blocks']:
                    print '  Blocked bugs: {}'.format(
                        ', '.join(map(str, bug.data['blocks'])))
                else:
                    print '  No blocked bugs'


@with_add_remove('given users', 'CC List', metavar='USER')
@with_bugs
@with_optional_message
class CC(Command):
    """Show or update CC List."""
    def __call__(self, args):
        bugs = map(self.bz.bug, args.bugs)
        if args.add or args.remove:
            # get actual users
            getuser = lambda x: self.bz.match_one_user(x)['name']
            add = map(getuser, args.add) if args.add else None
            remove = map(getuser, args.remove) if args.remove else None

            # get message
            message = editor.input('Enter your comment.') \
                if args.message is True else args.message

            # update CC list
            map(
                lambda x: self.bz.bug(x).update_cc(
                    add=add,
                    remove=remove,
                    comment=message
                ),
                args.bugs
            )
        else:
            # show CC List
            for bug in bugs:
                bug.read()
                print 'Bug {}:'.format(bug.bugno)
                if bug.data['cc']:
                    print '  CC List: {}'.format(
                        ', '.join(map(str, bug.data['cc'])))
                else:
                    print '  0 users'


@with_bugs
@with_optional_message
@with_limit(things='comments')
class Comment(Command):
    """List comments or file a comment on the given bugs."""
    args = [
        lambda x: x.add_argument('--reverse', action='store_true',
            default=True,
            help='Show from newest to oldest.'),
        lambda x: x.add_argument('--forward', action='store_false',
            dest='reverse',
            help='Show from oldest to newest.'),
    ]

    formatstring = '{}\nauthor: {creator}\ntime: {time}\n\n{text}\n\n'

    def __call__(self, args):
        message = editor.input('Enter your comment.') \
            if args.message is True else args.message
        if message:
            map(lambda x: self.bz.bug(x).add_comment(message), args.bugs)
        else:
            def cmtfmt(bug):
                comments = sorted(
                    enumerate(self.bz.bug(bug).get_comments()),
                    key=lambda x: int(x[1]['id']),
                    reverse=True  # initially reverse to apply limit
                )

                # apply limit, if one given
                comments = comments[:abs(args.limit)] \
                    if args.limit else comments

                # re-reverse if reversed comments were /not/ wanted
                comments = reversed(comments) if not args.reverse else comments

                return '=====\nBUG {}\n\n-----\n{}'.format(
                    bug,
                    '-----\n'.join(map(
                        lambda (n, x): self.formatstring.format(
                            'comment: {}'.format(n) if n else 'description',
                            **x
                        ),
                        comments
                    ))
                )
            print '\n'.join(map(cmtfmt, args.bugs))


@with_set('given bugs', 'depdendencies', metavar='BUG', type=int)
@with_add_remove('given bugs', 'depdendencies', metavar='BUG', type=int)
@with_bugs
@with_optional_message
class Depend(Command):
    """List or update bug dependencies."""
    def __call__(self, args):
        bugs = map(self.bz.bug, args.bugs)
        if args.add or args.remove or args.set:
            message = editor.input('Enter your comment.') \
                if args.message is True else args.message
            # update dependencies
            map(
                lambda x: x.update_depend(
                    add=args.add,
                    remove=args.remove,
                    set=args.set,
                    comment=message
                ),
                bugs
            )
        else:
            # show dependencies
            for bug in bugs:
                bug.read()
                print 'Bug {}:'.format(bug.bugno)
                if bug.data['depends_on']:
                    print '  Dependencies: {}'.format(
                        ', '.join(map(str, bug.data['depends_on'])))
                else:
                    print '  No dependencies'


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


#class New(Command):
#    """File a new bug."""
#    pass


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
@with_status
@with_resolution
@with_optional_message
class Status(Command):
    """Set the status of the given bugs."""
    def __call__(self, args):
        message = editor.input('Enter your comment.') if args.message is True \
            else args.message

        # get the values of the 'bug_status' field
        values = filter(
            lambda x: x['name'] == 'bug_status',
            self.bz.get_fields()
        )[0]['values']
        values = sorted(values, None, lambda x: int(x['sortkey']))

        if args.status:
            status = args.status.upper()
        else:
            # choose status
            status = self.ui.choose(
                'Choose a status',
                filter(None, map(lambda x: x['name'], values))
            )

        # check if the new status is "open"
        try:
            value = filter(lambda x: x['name'] == status, values)[0]
            is_open = value['is_open']
        except IndexError:
            # no value matching the chosen status
            raise UserWarning("Invalid status:", status)

        resolution = None
        if not is_open:
            # resolution required
            if args.resolution:
                resolution = args.resolution.upper()
            else:
                # choose resolution
                values = filter(
                    lambda x: x['name'] == 'resolution',
                    self.bz.get_fields()
                )[0]['values']
                values = sorted(values, None, lambda x: int(x['sortkey']))
                values = filter(None, map(lambda x: x['name'], values))
                resolution = self.ui.choose('Choose a resolution', values)

        return map(
            lambda x: self.bz.bug(x).set_status(
                status=status,
                resolution=resolution,
                comment=message
            ),
            args.bugs
        )


#class Search(Command):
#    """Search for bugs with supplied attributes."""
#    pass


# the list got too long; metaprogram it ^_^
commands = sorted(filter(
    lambda x: type(x) == type and issubclass(x, Command) and x is not Command,
    locals().viewvalues()
), None, lambda x: x.__name__)
