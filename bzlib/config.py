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

import ConfigParser
import os.path
import re


show_fields = [
    'alias', 'assigned_to', 'blocks', 'cc', 'creator', 'depends_on',
    'keywords', 'priority', 'component', 'resolution', 'status',
    'summary',
]


class ConfigError(Exception):
    pass


def check_section(section):
    if section in ['core', 'alias'] \
            or re.match(r'server\.\w+', section):
        return section
    raise ConfigError('invalid section: {}'.format(section))


class Config(ConfigParser.SafeConfigParser):
    _instances = {}

    @classmethod
    def get_config(cls, path):
        path = os.path.expanduser(path)
        if path not in cls._instances:
            cls._instances[path] = cls(path)
        return cls._instances[path]

    def __init__(self, path):
        path = os.path.expanduser(path)
        ConfigParser.SafeConfigParser.__init__(self)
        self._path = path
        self.read(self._path)

    def write(self):
        with open(self._path, 'w') as fp:
            ConfigParser.SafeConfigParser.write(self, fp)

    def add_section(self, section):
        ConfigParser.SafeConfigParser.add_section(self, check_section(section))


NoSectionError = ConfigParser.NoSectionError
