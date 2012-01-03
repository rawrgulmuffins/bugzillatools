# This file is part of bugzillatools
# Copyright (C) 2012 Fraser Tweedale
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

from . import ui


class FilterTestCase(unittest.TestCase):
    """Test filter functions."""

    def test_filter_int(self):
        # 'start' arg
        with self.assertRaisesRegexp(ui.InvalidInputError, 'value too small'):
            ui.filter_int('0', start=1)
        self.assertEqual(ui.filter_int('0', start=0), 0)

        # 'stop' arg
        with self.assertRaisesRegexp(ui.InvalidInputError, 'value too large'):
            ui.filter_int('2', stop=2)
        self.assertEqual(ui.filter_int('1', stop=2), 1)

        # bogus input
        with self.assertRaisesRegexp(ui.InvalidInputError, 'not an int'):
            ui.filter_int('a')

        # default
        with self.assertRaisesRegexp(ui.InvalidInputError, 'not an int'):
            ui.filter_int('')
        self.assertEqual(ui.filter_int('', default=100), 100)

    def test_filter_list(self):
        # no filter
        with self.assertRaisesRegexp(TypeError, r'\bfilter\b'):
            ui.filter_list('1 2 3')

        # duplicates
        with self.assertRaisesRegexp(
            ui.InvalidInputError,
            'duplicate values are not allowed'
        ):
            ui.filter_list(
                '1 1 1',
                filter=ui.filter_int,
                allow_duplicates=False
            )
        self.assertEqual(
            ui.filter_list(
                '1 1 1',
                filter=ui.filter_int,
                allow_duplicates=True,
                filter_duplicates=False
            ),
            [1, 1, 1]
        )
        self.assertEqual(
            ui.filter_list(
                '1 1 1',
                filter=ui.filter_int,
                allow_duplicates=True,
                filter_duplicates=True
            ),
            [1]
        )

        # min, max allowed
        with self.assertRaisesRegexp(ui.InvalidInputError, 'too few'):
            ui.filter_list('1 2 3', filter=ui.filter_int, min_allowed=4)
        ui.filter_list('1 2 3', filter=ui.filter_int, min_allowed=3)
        with self.assertRaisesRegexp(ui.InvalidInputError, 'too many'):
            ui.filter_list('1 2 3', filter=ui.filter_int, max_allowed=2)
        ui.filter_list('1 2 3', filter=ui.filter_int, max_allowed=3)

        # bogus values
        with self.assertRaises(ui.InvalidInputError):
            ui.filter_list('a b c', filter=ui.filter_int)

        # delimiter checks
        self.assertEqual(
            ui.filter_list(' 1,,2::3;;4  5\t\t6:;,7 ', filter=ui.filter_int),
            [1, 2, 3, 4, 5, 6, 7]
        )
        self.assertEqual(ui.filter_list(' ', filter=ui.filter_int), [])

        # empty (no default)
        self.assertEqual(ui.filter_list('', filter=ui.filter_int), [])

        # empty (with default)
        self.assertEqual(
            ui.filter_list('', filter=ui.filter_int, default=[3, 2, 1]),
            [3, 2, 1]
        )
