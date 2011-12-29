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

import urlparse
import xmlrpclib

from . import bug
from . import config


# field type constants
FIELD_UNKNOWN = 0
FIELD_TEXT = 1
FIELD_SELECT = 2
FIELD_SELECT_MULTIPLE = 3
FIELD_TEXTAREA = 4
FIELD_DATETIME = 5
FIELD_BUG_ID = 6
FIELD_BUG_URL = 7


class UserError(Exception):
    pass


class URLError(Exception):
    pass


class Bugzilla(object):
    """A Bugzilla server."""

    __slots__ = [
        '_products', '_fields', '_user_cache',
        'url', 'user', 'password', 'config',
        'server',
    ]

    @classmethod
    def from_config(cls, conf, **kwargs):
        """Instantiate a Bugzilla according to given Config and args.

        The 'server', 'url', 'user' and 'password' keyword arguments are
        required, but may be ``None``.
        """
        mandatory_args = set(['server', 'url', 'user', 'password'])
        mandatory_args -= kwargs.viewkeys()
        if mandatory_args:
            raise TypeError('Mandatory args ({}) not supplied'.format(
                ', '.join("'{}'".format(arg) for arg in mandatory_args)))

        if kwargs['server'] is None and conf.has_option('core', 'server'):
            kwargs['server'] = conf.get('core', 'server')

        _server = {}
        if kwargs['server']:
            try:
                _server = dict(conf.items('server.' + kwargs['server']))
            except config.NoSectionError:
                raise UserWarning(
                    "No configuration for server '{}'."
                    .format(kwargs['server'])
                )
        _server.update(
            {k: kwargs[k] for k in ('url', 'user', 'password') if kwargs[k]}
        )
        return cls(**_server)

    def __init__(self, url=None, user=None, password=None, **config):
        """Create a Bugzilla XML-RPC client.

        url      : points to a bugzilla instance (base URL; must end in '/')
        user     : bugzilla username
        password : bugzilla password
        """

        self._products = None
        self._fields = None
        self._user_cache = {}

        self.url = url
        self.user = user
        self.password = password
        self.config = config

        parsed_url = urlparse.urlparse(url)
        if not parsed_url.netloc:
            raise URLError('URL {!r} is not valid.'.format(url))
        if parsed_url.scheme not in ('http', 'https'):
            raise URLError(
                'URL scheme {!r} not supported.'.format(parsed_url.scheme)
            )
        if parsed_url.params or parsed_url.query or parsed_url.fragment:
            raise URLError(
                'URL params, queries and fragments not supported.'
            )
        url = url + 'xmlrpc.cgi' if url[-1] == '/' else url + '/xmlrpc.cgi'
        # httplib explodes if url is unicode
        self.server = xmlrpclib.ServerProxy(str(url), use_datetime=True)

    def rpc(self, *args, **kwargs):
        """Do an RPC on the Bugzilla server.

        args: RPC method, in fragments
        kwargs: RPC parameters
        """
        kwargs['Bugzilla_login'] = self.user
        kwargs['Bugzilla_password'] = self.password

        method = self.server
        for fragment in args:
            method = getattr(method, fragment)
        return method(kwargs)

    def bug(self, bugno):
        """Extrude a Bug object."""
        return bug.Bug(self, bugno)

    def get_products(self, use_cache=True):
        """Get accessible products of this Bugzilla."""
        if use_cache and self._products:
            return self._products
        ids = self.rpc('Product', 'get_accessible_products')['ids']
        self._products = self.rpc('Product', 'get', ids=ids)['products']
        return self._products

    def get_fields(self, use_cache=True):
        """Get information about bug fields."""
        if use_cache and self._fields:
            return self._fields
        self._fields = self.rpc('Bug', 'fields')['fields']
        return self._fields

    def get_field_values(self,
        name,
        sort=True,
        omit_empty=True,
        visible_for=None
    ):
        """Return the legal values for a field; a list of dicts.

        visible_for:
            A dict of bug data.  If the field has a value_field and its value
            is a key in the dict, the value of that bug field will be used to
            filter the values of field being queried accord to the contents of
            visibility_values.  If the field does not have a value_field, no
            effect.  If not supplied, no effect.
        """
        field = filter(lambda x: x['name'] == name, self.get_fields())[0]
        values = field['values']
        if omit_empty:
            values = filter(lambda x: x['name'], values)
        value_field = field.get('value_field')
        if visible_for and value_field and value_field in visible_for:
            visibility_value = visible_for[value_field]
            values = filter(
                lambda x: visibility_value in x['visibility_values'],
                values
            )
        if sort:
            values = sorted(values, key=lambda x: int(x['sortkey']))
        return values

    def match_users(self, fragment, use_cache=True):
        """Return a list of users matching the given string."""
        if use_cache and fragment in self._user_cache:
            return self._user_cache[fragment]
        users = self.rpc('User', 'get', match=[fragment])['users']
        if use_cache:
            self._user_cache[fragment] = users
        return users

    def match_one_user(self, fragment, use_cache=True):
        """Return the user matching the given string.

        Raise UserError if the result does not contain exactly one user.
        """
        users = self.match_users(fragment)
        if not users:
            raise UserError("No users matching '{}'".format(fragment))
        if len(users) > 1:
            raise UserError("Multiple users matching '{}': {}".format(
                fragment,
                ', '.join(map(lambda x: x['name'], users))
            ))
        return users[0]
