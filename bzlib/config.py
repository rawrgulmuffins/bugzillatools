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

import json
import os.path


show_fields = [
    'alias', 'assigned_to', 'blocks', 'cc', 'creator', 'depends_on',
    'keywords', 'priority', 'component', 'resolution', 'status',
    'summary',
]

default = {}


def read_config():
    f = os.path.expanduser('~/.bugzillarc')
    if not os.path.isfile(f):
        # file doesn't exist; empty config
        return None
    with open(f) as fh:
        return json.load(fh)

config = read_config()


def get(key):
    if not config:
        return None
    return config.get(key) or default.get(key)


def get_show_fields():
    return set(show_fields) \
        - set(get('ignore_fields') or []) \
        | set(get('show_fields') or [])
