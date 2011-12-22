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

import socket
import unittest

from . import bugzilla
from . import bug


class BugTestCase(unittest.TestCase):
    def setUp(self):
        self.bz = bugzilla.Bugzilla('http://bugzilla.example.com/', 'u', 'p')

    def test_search(self):
        with self.assertRaisesRegexp(TypeError, r'\bfoobar\b'):
            bug.Bug.search(self.bz, foobar='baz')
        with self.assertRaisesRegexp(TypeError, r'\bfoobar\b'):
            bug.Bug.search(self.bz, not_foobar='baz')
        fields = frozenset([
            'alias', 'assigned_to', 'component', 'creation_time', 'creator',
            'id', 'last_change_time', 'op_sys', 'platform', 'priority',
            'product', 'resolution', 'severity', 'status', 'summary',
            'target_milestone', 'qa_contact', 'url', 'version', 'whiteboard',
            'limit', 'offset',
        ])
        with self.assertRaises(socket.gaierror):
            bug.Bug.search(self.bz, **{field: 'foo' for field in fields})
        with self.assertRaises(socket.gaierror):
            bug.Bug.search(
                self.bz,
                **{field: 'not_' + 'foo' for field in fields}
            )
