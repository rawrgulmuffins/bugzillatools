# This file is part of bugzillatools
# Copyright (C) 2011 Fraser Tweedale, Benon Technologies Pty Ltd
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

import itertools
import os
import tempfile
import unittest

from . import bugzilla
from . import config


class URLTestCase(unittest.TestCase):
    """Test Bugzilla URL handling."""

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


class FromConfigTestCase(unittest.TestCase):
    def setUp(self):
        fd, self._path = tempfile.mkstemp()
        os.close(fd)
        with open(self._path, 'w') as f:
            f.write(
                '[core]\n'
                'server = test\n'
                '[server.test]\n'
                'url = http://bugzilla.example.com/\n'
                'user = jbloggs\n'
                'password = letmein\n'
                'foo = bar\n'
            )
        self._conf = config.Config.get_config(self._path)

    def tearDown(self):
        del self._conf
        os.remove(self._path)
        del self._path

    def test_from_config_type(self):
        """Test that all mandatory args are checked."""
        mandatory_args = set(['server', 'url', 'user', 'password'])
        for args in itertools.combinations(mandatory_args, 2):
            with self.assertRaisesRegexp(TypeError, '[Mm]andatory'):
                bugzilla.Bugzilla.from_config(
                    self._conf,
                    **{k: None for k in args}
                )
        kwargs = {k: None for k in mandatory_args}
        kwargs['server'] = 'test'

    def test_from_config(self):
        """Test that from_config produces correctly initialised instance."""
        mandatory_args = set(['server', 'url', 'user', 'password'])
        kwargs = {k: None for k in mandatory_args}
        kwargs['server'] = 'test'
        bz = bugzilla.Bugzilla.from_config(self._conf, **kwargs)
        self.assertEqual(bz.url, 'http://bugzilla.example.com/')
        self.assertEqual(bz.user, 'jbloggs')
        self.assertEqual(bz.password, 'letmein')
        self.assertEqual(bz.config, {'foo': 'bar'})

    def test_from_config_with_default_server(self):
        """Test that the default server gets used."""
        mandatory_args = set(['server', 'url', 'user', 'password'])
        kwargs = {k: None for k in mandatory_args}
        bz = bugzilla.Bugzilla.from_config(self._conf, **kwargs)
        self.assertEqual(bz.url, 'http://bugzilla.example.com/')
