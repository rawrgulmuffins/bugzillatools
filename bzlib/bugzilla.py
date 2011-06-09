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

import re
import xmlrpclib

from . import bug


class Bugzilla(object):

    def __init__(self, url, user, password):
        """Create a Bugzilla XML-RPC client.

        url      : points to a bugzilla instance (base URL; must end in '/')
        user     : bugzilla username
        password : bugzilla password
        """

        self.user = user
        self.password = password

        match = re.match('http://.*?/', url)
        self.server = xmlrpclib.ServerProxy(match.group(0) + 'xmlrpc.cgi')

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
