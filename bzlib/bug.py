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

import datetime


class Bug(object):

    @property
    def data(self):
        if self._data is None:
            if not self.bugno:
                raise Exception("bugno not provided.")
            self._data = self.rpc('get', ids=[self.bugno])['bugs'][0]
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def comments(self):
        if self._comments is None:
            if not self.bugno:
                raise Exception("bugno not provided.")
            result = self.rpc('comments', ids=[self.bugno])
            self._comments = result['bugs'][str(self.bugno)]['comments']
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    @classmethod
    def search(cls, bz, args):
        pass

    def __init__(self, bz, bugno_or_data=None):
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
        try:
            self.bugno = int(bugno_or_data)
        except TypeError:
            self.data = bugno_or_data or {}

    def rpc(self, *args, **kwargs):
        """Does an RPC on the Bugzilla server.

        Prepends 'Bug' to the method name.
        """
        return self.bz.rpc(*(('Bug',) + args), **kwargs)

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

        Return the new bug ID.
        """
        if self.bugno or 'id' in self.data:
            raise Exception("bugno is known; not creating bug.")
        result = self.rpc('create', **self.data)
        self.bugno = result['id']
        return self.bugno

    def add_comment(self, comment):
        self.rpc('add_comment', id=self.bugno, comment=comment)
        self.comments = None  # comments are stale

    def is_open(self):
        """Return True if the bug is open, otherwise False."""
        return self.data['is_open']

    def set_dupe_of(self, bug, comment=None):
        """Set this bug a duplicate of the given bug."""
        kwargs = {'dupe_of': bug}
        if comment:
            kwargs['comment'] = {'body': comment}
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
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
        match=True
    ):
        """Reassign this bug.

        user: the new assignee
        comment: optional comment
        match: search for a user matching the given string

        If the ``assign_status`` config is set for the ``Bugzilla`` and
        the current status matches the first value, the status will be
        updated to the second value.
        """
        if match:
            user = self.bz.match_one_user(user)['name']
        kwargs = {'assigned_to': user}
        if comment:
            kwargs['comment'] = {'body': comment}
        if 'assign_status' in self.bz.config:
            try:
                froms, to = self.bz.config['assign_status'].split()
                if self.data['status'] in froms.split(','):
                    kwargs['status'] = to
            except:
                pass  # ignore errors (incorrect config)
        self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if comment:
                self.comments = None  # comments are stale

    def update(self, **kwargs):
        """Update the bug.

        A wrapper for the RPC ``bug.update`` method that performs some sanity
        checks and flushes cached data as necessary.
        """
        fields = frozenset([
            'remaining_time', 'work_time', 'estimated_time', 'deadline',
            'blocks', 'depends_on',
            'cc',
            'comment',
        ])
        unknowns = kwargs.viewkeys() - fields
        if unknowns:
            # unknown arguments
            raise TypeError('Invalid keyword arguments: {}.'.format(unknowns))

        # filter out ``None``s
        kwargs = {k: v for k, v in kwargs.viewitems() if v is not None}

        # format deadline (YYYY-MM-DD)
        if 'deadline' in kwargs:
            date = kwargs['deadline']
            if isinstance(date, datetime.datetime):
                date = date.date()  # get date component of a datetime
            kwargs['deadline'] = str(date)  # datetime.date formats in ISO

        result = self.rpc('update', ids=[self.bugno], **kwargs)
        self.data = None  # data is stale
        if 'comment' in kwargs:
            self.comments = None  # comments are stale
        return result
        # TODO refactor other methods to use this

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
