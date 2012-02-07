# This file is part of bugzillatools
# Copyright (C) 2011, 2012 Benon Technologies Pty Ltd, Fraser Tweedale
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

version_info = (0, 5, 2, 'final', 0)

version_fmt = '{0}.{1}'
if version_info[2]:
    version_fmt += '.{2}'
if version_info[3] != 'final':
    version_fmt += '{3}{4}'
version = version_fmt.format(*version_info)
