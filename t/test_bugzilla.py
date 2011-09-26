import unittest

import bzlib.bugzilla


class URLTestCase(unittest.TestCase):
    def testScheme(self):
        # http
        self.assertIsInstance(
            bzlib.bugzilla.Bugzilla('http://bugzilla.example.com/', 'u', 'p'),
            bzlib.bugzilla.Bugzilla
        )
        # https
        self.assertIsInstance(
            bzlib.bugzilla.Bugzilla('https://bugzilla.example.com/', 'u', 'p'),
            bzlib.bugzilla.Bugzilla
        )
        # bogus scheme
        with self.assertRaises(bzlib.bugzilla.URLError) as cm:
            bzlib.bugzilla.Bugzilla('bogus://bugzilla.example.com/', 'u', 'p')
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
            with self.assertRaises(bzlib.bugzilla.URLError) as cm:
                bzlib.bugzilla.Bugzilla(url, 'u', 'p')
            self.assertEqual(
                cm.exception.message,
                'URL {!r} is not valid.'.format(url)
            )

    def testParamQueryFragment(self):
        # param
        with self.assertRaises(bzlib.bugzilla.URLError) as cm:
            bzlib.bugzilla.Bugzilla('http://bugzilla.example.com/;p', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )
        # query
        with self.assertRaises(bzlib.bugzilla.URLError) as cm:
            bzlib.bugzilla.Bugzilla('http://bugzilla.example.com/?q', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )
        # fragment
        with self.assertRaises(bzlib.bugzilla.URLError) as cm:
            bzlib.bugzilla.Bugzilla('http://bugzilla.example.com/#f', 'u', 'p')
        self.assertEqual(
            cm.exception.message,
            'URL params, queries and fragments not supported.'
        )

    def testXMLRPC(self):
        host = 'bugzilla.example.com'

        # no trailing '/'
        bz = bzlib.bugzilla.Bugzilla('http://' + host, 'u', 'p')
        self.assertEquals(bz.server._ServerProxy__host, host)
        self.assertEquals(bz.server._ServerProxy__handler, '/xmlrpc.cgi')

        # trailing '/'
        bz = bzlib.bugzilla.Bugzilla('http://' + host + '/', 'u', 'p')
        self.assertEquals(bz.server._ServerProxy__host, host)
        self.assertEquals(bz.server._ServerProxy__handler, '/xmlrpc.cgi')
