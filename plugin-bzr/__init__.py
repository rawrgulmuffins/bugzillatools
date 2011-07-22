# This file is part of bugzillatools
# Copyright (C) 2010-2011 Benon Technologies Pty Ltd
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

"""Mark bugzilla bugs fixed using --fixes argument.

Description
-----------

This plugin, when enabled for Bugzilla bugtrackers, marks bugs fixed on
those trackers when ``bzr commit`` is invoked with the ``--fixes`` argument.
It also adds a comment to the bug that includes the branch location, the
commit message, the list of changed files and other details about the commit.

Configuration
-------------

Define the bugtracker in your ``bazaar.conf`` in the normal fashion, and
enable *bugzillatools* for that tracker.

    bugzilla_<handle>_url = <url>
    bugzilla_<handle>_bugzillatools_enable = True

The type of ``bugzilla_<handle>_bugzillatools_enable`` is actually string,
not boolean, so to explicitly disable the plugin leave the line blank after
the ``=``.

If the handle matches a server in your ``.bugzillarc``, no further
configuration is needed; the parameters from this file will be used.  The
URLs should not differ between the two configuration files, but if they do,
``.bugzillarc`` takes precendence.

If the handle does not match a server in your ``.bugzillarc``, the Bugzilla
URL, user and password are determined thusly:

- For the url, the value of ``bugzilla_<handle>_url``.
- For the username, ``bugzilla_<handle>_user`` or if this is not defined, the
  email address of the committer.
- For the password, ``bugzilla_<handle>_password``, which must be defined.

The status and resolution of "fixed" bugs must also be specified for each
tracker, since these are configurable and may differ between installations
of Bugzilla.  For example, in your ``bazaar.conf``::

    bugzilla_<handle>_status = RESOLVED
    bugzilla_<handle>_resolution = FIXED

Example
-------

A Bugzilla server at ``http://bugzilla.example.com``, with user
``bob@example.com`` and password ``bob123``.

``.bugzillarc``::

    ...
    "servers": {
        "example": ["http://bugzilla.example.com", "bob@example.com", "bob123"]
    }
    ...

``bazaar.conf``::

    bugzilla_example_url = http://bugzilla.example.com/
    bugzilla_example_bugzillatools_enable = True
    bugzilla_example_status = RESOLVED
    bugzilla_example_resolution = FIXED

If not defining ``example`` in ``.bugzillarc``, also include::

    bugzilla_example_password = bob123

and, if Bob is not committing as ``bob@example.com``, also include::

    bugzilla_example_user = bob@example.com

To mark a bug fixed (in addition to the standard behaviour of recording
a bug URL and status in the revision metadata), invoke Bazaar thusly::

    bzr commit -m 'fix bug 123' --fixes example:123
"""

import bzrlib.api
import bzrlib.commands
import bzrlib.trace

import bzlib

from . import hooks

# plugin setup
version_info = bzlib.version_info

COMPATIBLE_BZR_VERSIONS = [
    (2, 0, 0),
    (2, 1, 0),
    (2, 2, 0),
    (2, 3, 0),
]

bzrlib.api.require_any_api(bzrlib, COMPATIBLE_BZR_VERSIONS)

if __name__ != 'bzrlib.plugins.bugzillatools':
    bzrlib.trace.warning(
        'Not running as bzrlib.plugins.bugzillatools; things may break.')

# install the get_command hook
bzrlib.commands.Command.hooks.install_named_hook(
    'get_command',
    hooks.get_command_hook,
    'bugzilla plugin - extend cmd_commit'
)
