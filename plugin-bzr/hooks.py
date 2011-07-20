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

import functools
import StringIO

import bzrlib.builtins
import bzrlib.branch
import bzrlib.bugtracker
import bzrlib.config
import bzrlib.log


def post_commit_hook(
    local,
    master,
    old_revno,
    old_revid,
    new_revno,
    new_revid,
    fixes=None
):
    """This hook modifies bugzilla trackers according to --fixes."""
    fixes = fixes or []

    branch = local or master
    config = branch.get_config()
    revision = branch.repository.get_revision(new_revid)

    # store bugzilla tasks
    bugz = []

    for fix in fixes:

        # since we got to post_commit, we can assume the handles are valid
        tag, bug = fix.split(':')
        tracker = bzrlib.bugtracker.tracker_registry.get_tracker(tag, branch)
        UPIBT = bzrlib.bugtracker.URLParametrizedIntegerBugTracker
        if not isinstance(tracker, UPIBT) or tracker.type_name != 'bugzilla':
            continue  # not a bugzilla

        # get bugzilla credentials for this tracker
        #   user defaults to email address of committer
        user = config.get_user_option('bugzilla_%s_user' % tag) \
                or bzrlib.config.extract_email_address(revision.committer)
        #   no default for password; if not supplied, we skip
        password = config.get_user_option('bugzilla_%s_password' % tag)
        if not password:
            continue

        # find the matching revprop
        # this code isn't really required right now, given that the only
        # valid status is 'fixed', but if more are added, this will
        # provide the appropriate filtering
        for url, status in revision.iter_bugs():
            if url != tracker.get_bug_url(bug):
                continue  # not this bugtracker
            if status != bzrlib.bugtracker.FIXED:
                continue  # not a fixed bug

            # fix matches a bugzilla bug and status is 'fixed'
            # append the task to bugz
            bugz.append([bug, url, user, password, status])

    if bugz:
        outf = StringIO.StringIO()
        # show master branch (i.e. bound location if a bound branch)
        outf.write('Fixed in commit at:\n %s\n\n' % master.base)
        lf = bzrlib.log.log_formatter('long', show_ids=True, to_file=outf)
        bzrlib.log.show_log(
            branch,
            lf,
            start_revision=new_revno,
            end_revision=new_revno,
            verbose=True
        )
        msg = outf.getvalue()
        print 'message:\n', msg

        for bug, url, user, password, status in bugz:
            print 'marking %s %s as %s' % (url, status, user)
            # TODO move to bzlib
            bz = bugzilla.Bugzilla(url, user, password)
            if status == bzrlib.bugtracker.FIXED:
                if not bz.fix(bug, msgw):
                    print 'ERROR: unable to mark bug fixed'


def get_command_hook(cmd_or_None, command_name):
    """Enhance the ``commit`` command."""
    if isinstance(cmd_or_None, bzrlib.builtins.cmd_commit):
        class cmd_commit(type(cmd_or_None)):
            """Commit command that saves bug state.

            This is a tiny shim around the builtin commit command that
            simply saves information about fixed bugs (if any are given
            on the command line) for later use in the post_commit hook
            provided by this plugin.
            """
            def __init__(self, *args, **kwargs):
                self.__doc__ = super(cmd_commit, self).__doc__
                super(cmd_commit, self).__init__(*args, **kwargs)

            def run(self, *args, **kwargs):
                if kwargs['fixes']:
                    # curry the post-commit hook with fixes and install it
                    bzrlib.branch.Branch.hooks.install_named_hook(
                        'post_commit',
                        functools.partial(
                            post_commit_hook,
                            fixes=kwargs['fixes']
                        ),
                        'Check fixed bugs'
                    )
                super(cmd_commit, self).run(*args, **kwargs)

        return cmd_commit()

    return cmd_or_None
