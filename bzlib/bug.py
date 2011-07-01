# This file is part of bugzillatools
# Copyright (C) 2011 Benon Technologies Pty Ltd
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


class Bug(object):

    @classmethod
    def search(cls, bz, args):
        pass

    def __init__(self, bz, bugno_or_data):
        """Create a bug object.

        bz: a bzlib.Bugzilla object
        bugno_or_data: if an int, refers to bugno, otherwise implies a
                       new bug with the given data, otherwise implies
                       a new bug with no data (yet).
        If data is None (the default) and if bugno is set, the data will be
        retrieved lazily.
        """
        self.bz = bz

        self.bugno = None
        self.data = None
        self.comments = None
        if isinstance(bugno_or_data, int):
            self.bugno = bugno_or_data
        elif bugno_or_data:
            self.data = bugno_or_data

    def rpc(self, *args, **kwargs):
        """Does an RPC on the Bugzilla server.

        Prepends 'Bug' to the method name.
        """
        return self.bz.rpc(*(('Bug',) + args), **kwargs)

    def read(self):
        """Read bug data, unless already read."""
        if not self.bugno:
            raise Exception("bugno not provided.")
        if not self.data:
            self.data = self.rpc('get', ids=[self.bugno])['bugs'][0]

    def read_comments(self):
        """Read bug comments, unless already read."""
        if not self.bugno:
            raise Exception("bugno not provided.")
        if not self.comments:
            key = str(self.bugno)
            self.comments = \
                self.rpc('comments', ids=[self.bugno])['bugs'][key]['comments']

    def create(self):
        """Create a new bug.

        Required fields are:
          - product
          - component
          - summary
          - version

        Optional fields that may be useful include:
          - assigned_to
          - status
          - priority
          - cc
        """
        if self.bugno or 'id' in self.data:
            raise Exception("bugno is known; not creating bug.")
        result = self.rpc('create', **self.data)
        self.bugno = result['id']

    def get_comments(self):
        self.read_comments()
        return self.comments

    def add_comment(self, comment):
        self.rpc('add_comment', id=self.bugno, comment=comment)
        self.comments = None  # comments are stale

    def set_status(self, status, resolution='', comment=None):
        """Set the status of this bug.

        A resolution string should be included for those statuses where it
        makes sense.

        A comment may optionally accompany the status change.
        """
        kwargs = {'status': status}
        if resolution:
            kwargs['resolution'] = resolution
        if comment:
            kwargs['comment'] = {'body': comment}
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
            self.comments = None  # comments are stale

    def set_assigned_to(
        self,
        user,
        comment=None,
        update_status=True,
        match=True
    ):
        """Reassign this bug.

        user: the new assignee
        comment: optional comment
        update_status: change status to ASSIGNED, iff status is currently NEW
        match: search for a user matching the given string
        """
        if match:
            user = self.bz.match_one_user(user)['name']
        kwargs = {'assigned_to': user}
        if comment:
            kwargs['comment'] = {'body': comment}
        # TODO if comment is None, automatically construct comment?
        if update_status:
            # check current status
            if not self.data:
                self.read()
            if self.data['status'] == 'NEW':
                kwargs['status'] = 'ASSIGNED'
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
                self.comments = None  # comments are stale

    def update_block(self, add=None, remove=None, set=None, comment=None):
        """Update the bugs that this bug blocks.

        Accepts arrays of integer bug numbers.
        """
        blocks = {}
        if set:
            blocks['set'] = set
        else:
            if add:
                blocks['add'] = add
            if remove:
                blocks['remove'] = remove
        kwargs = {'blocks': blocks}
        if comment:
            kwargs['comment'] = {'body': comment}
        # TODO if comment is None, automatically construct comment?
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
            self.comments = None  # comments are stale

    def update_depend(self, add=None, remove=None, set=None, comment=None):
        """Update the bugs on which this bug depends.

        Accepts arrays of integer bug numbers.
        """
        depends = {}
        if set:
            depends['set'] = set
        else:
            if add:
                depends['add'] = add
            if remove:
                depends['remove'] = remove
        kwargs = {'depends_on': depends}
        if comment:
            kwargs['comment'] = {'body': comment}
        # TODO if comment is None, automatically construct comment?
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
            self.comments = None  # comments are stale

    def update_cc(self, add=None, remove=None, comment=None):
        """Update the CC list of the given bugs.

        Accepts arrays of valid user names.
        """
        cc = {}
        if add:
            cc['add'] = add
        if remove:
            cc['remove'] = remove
        if not cc:
            return  # nothing to do
        kwargs = {'cc': cc}
        if comment:
            kwargs['comment'] = {'body': comment}
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
            self.comments = None  # comments are stale
