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

import os
import subprocess
import tempfile
import textwrap


class EmptyInputError(Exception):
    pass


def input(message, remove_comments=True):
    """Invoke $EDITOR for message input.

    Invoke $EDITOR or /bin/vi on a temporary file for user input.

    message: A message describing what the user is inputting. Should be
             terminated with a full stop.
    remove_comments: Remove lines starting with '#' from the data.
    """
    try:
        editor = os.environ['EDITOR']
    except KeyError:
        editor = '/bin/vi'

    # build initial text
    text = [message]
    if remove_comments:
        text.append("Lines starting with '#' will be ignored.")
    text.append('An empty message aborts the operation.')

    lines = ['\n']  # start with a single empty line
    lines += map(lambda x: '# ' + x + '\n', textwrap.wrap(' '.join(text)))

    with tempfile.NamedTemporaryFile() as fh:
        fh.writelines(lines)
        fh.flush()
        returncode = subprocess.call([editor, fh.name])
        if returncode:
            raise IOError('Editor did not exit cleanly')
        fh.seek(0)
        lines = fh.readlines()
        if remove_comments:
            lines = filter(lambda x: not x or x[0] != '#', lines)
        if not lines or not lines[0] and len(lines) == 1:
            # no lines, or a single empty line
            raise EmptyInputError()
        return ''.join(lines)
