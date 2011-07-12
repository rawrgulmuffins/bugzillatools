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

import xmlrpclib

from . import bug


class UserError(Exception):
    pass


class Bugzilla(object):

    _fields = None
    _user_cache = {}

    def __init__(self, url, user, password):
        """Create a Bugzilla XML-RPC client.

        url      : points to a bugzilla instance (base URL; must end in '/')
        user     : bugzilla username
        password : bugzilla password
        """

        self.user = user
        self.password = password

        # TODO URL sanity checks
        url = url[:-1] if url[-1] == '/' else url  # strip trailing slash
        # httplib explodes if url is unicode
        self.server = xmlrpclib.ServerProxy(str(url + '/xmlrpc.cgi'))

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

    def get_fields(self, use_cache=True):
        """Get information about bug fields."""
        if use_cache and self._fields:
            return self._fields
        self._fields = self.rpc('Bug', 'fields')['fields']
        return self._fields

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
