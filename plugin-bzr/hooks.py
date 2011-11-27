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

import bzlib.bugzilla
import bzlib.config

import bzrlib.builtins
import bzrlib.branch
import bzrlib.bugtracker
import bzrlib.config
import bzrlib.log
import bzrlib.trace

conf = bzlib.config.Config.get_config('~/.bugzillarc')


def post_commit_hook(
    local, master, old_revno, old_revid, new_revno, new_revid,  # bzrlib args
    fixes=None  # this one get curried using functools.partial
):
    """This hook marks fixed bugzilla bugs specified by --fixes arguments."""
    branch = local or master
    config = branch.get_config()
    revision = branch.repository.get_revision(new_revid)
    status_by_url = dict(revision.iter_bugs())

    # store bugzilla tasks
    bugs = []

    # since we made it to post-commit, all the bugtracker handles are valid
    for tag, bug in map(lambda x: x.split(':'), fixes or []):
        enabled = config.get_user_option(
            'bugzilla_%s_bugzillatools_enable' % tag
        )
        if not enabled:
            continue  # bugzillatools not enabled for this tracker

        tracker = bzrlib.bugtracker.tracker_registry.get_tracker(tag, branch)
        UPIBT = bzrlib.bugtracker.URLParametrizedIntegerBugTracker
        if not isinstance(tracker, UPIBT) or tracker.type_name != 'bugzilla':
            continue  # tracker is not a bugzilla tracker

        if status_by_url[tracker.get_bug_url(bug)] != bzrlib.bugtracker.FIXED:
            # bzrlib only groks fixed for now, but if other statuses come
            # along this will filter them out
            continue

        # see if bzlib knows about this server
        url, user, password = None, None, None
        try:
            server = dict(conf.items('server.' + tag))
            url, user, password = \
                [server.get(k) for k in 'url', 'user', 'password']
        except bzlib.config.NoSectionError:
            pass  # server not defined

        # url falls back to bzr config (tracker url)
        #
        # ugly hack: API doesn't expose the tracker URL, but _base_url property
        # is defined for URLParametrizedBugTracker, which bugzilla trackers are
        url = url or tracker._base_url

        # user falls back to bzr config, then committer
        user = user \
            or config.get_user_option('bugzilla_%s_user' % tag) \
            or bzrlib.config.extract_email_address(revision.committer)

        # password falls back to bzr config
        password = password \
            or config.get_user_option('bugzilla_%s_password' % tag)
        if not password:
            bzrlib.trace.warning(
                "Password not defined for bugtracker '{}'.".format(tag)
            )
            continue

        # get status and resolution
        status = config.get_user_option('bugzilla_%s_status' % tag)
        resolution = config.get_user_option('bugzilla_%s_resolution' % tag)
        if not (status and resolution):
            bzrlib.trace.warning(
                "Status or resolution not defined for bugtracker '{}'.".format(
                    tag
                )
            )
            continue

        bugs.append([bug, url, user, password, status, resolution])

    if not bugs:
        return  # nothing to do

    # assemble the comment
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

    for bug, url, user, password, status, resolution in bugs:
        print 'Setting status of bug {} on {} to {} {}'.format(
            bug, url, status, resolution
        )
        bz = bzlib.bugzilla.Bugzilla(url, user, password)
        try:
            bz.bug(bug).set_status(status, resolution, msg)
        except Exception as e:
            bzrlib.trace.show_error('Bugtracker error: ' + str(e))


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
