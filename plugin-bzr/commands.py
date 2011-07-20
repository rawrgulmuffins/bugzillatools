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

import bzrlib.branch
import bzrlib.builtins

from . import fixes
from . import hooks


class cmd_commit(bzrlib.builtins.cmd_commit):
    """Commit command that saves bug state.

    This is a tiny shim around the builtin commit command that simply
    saves information about fixed bugs (if any are given on the command
    line) for later use in the post_commit hook provided by this plugin.
    """

    def __init__(self, *args, **kwargs):
        self.__doc__ = super(cmd_commit, self).__doc__
        super(cmd_commit, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        if 'review' in kwargs:
            fixes.review = kwargs.pop('review')
        if kwargs['fixes']:
            # save the fixes
            fixes.fixes = kwargs['fixes']
            # install the post_commit hook
            bzrlib.branch.Branch.hooks.install_named_hook(
                'post_commit',
                hooks.post_commit_hook,
                'Check fixed bugs'
            )
        super(cmd_commit, self).run(*args, **kwargs)
