# This file is part of bugzillatools
# Copyright (C) 2011 Fraser Tweedale
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

import unittest

from . import bugzilla


class URLTestCase(unittest.TestCase):
    def testScheme(self):
        # http
        self.assertIsInstance(
            bugzilla.Bugzilla('http://bugzilla.example.com/', 'u', 'p'),
            bugzilla.Bugzilla
        )
        # https
        self.assertIsInstance(
            bugzilla.Bugzilla('https://bugzilla.example.com/', 'u', 'p'),
            bugzilla.Bugzilla
        )
        # bogus scheme
        with self.assertRaises(bugzilla.URLError) as cm:
            bugzilla.Bugzilla('bogus://bugzilla.example.com/', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            "URL scheme 'bogus' not supported."
        )

    def testNetloc(self):
        urls = [
            '',
            'http:example.com'
        ]
        for url in urls:
            with self.assertRaises(bugzilla.URLError) as cm:
                bugzilla.Bugzilla(url, 'u', 'p')
            self.assertEqual(
                cm.exception.message,
                'URL {!r} is not valid.'.format(url)
            )

    def testParamQueryFragment(self):
        # param
        with self.assertRaises(bugzilla.URLError) as cm:
            bugzilla.Bugzilla('http://bugzilla.example.com/;p', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )
        # query
        with self.assertRaises(bugzilla.URLError) as cm:
            bugzilla.Bugzilla('http://bugzilla.example.com/?q', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )
        # fragment
        with self.assertRaises(bugzilla.URLError) as cm:
            bugzilla.Bugzilla('http://bugzilla.example.com/#f', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )

    def testXMLRPC(self):
        host = 'bugzilla.example.com'

        # no trailing '/'
        bz = bugzilla.Bugzilla('http://' + host, 'u', 'p')
        self.assertEquals(bz.server._ServerProxy__host, host)
        self.assertEquals(bz.server._ServerProxy__handler, '/xmlrpc.cgi')

        # trailing '/'
        bz = bugzilla.Bugzilla('http://' + host + '/', 'u', 'p')
        self.assertEquals(bz.server._ServerProxy__host, host)
        self.assertEquals(bz.server._ServerProxy__handler, '/xmlrpc.cgi')
