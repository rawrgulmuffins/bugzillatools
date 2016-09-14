bugzillatools consists of the ``bugzilla`` CLI program and a Python
library for interacting with the Bugzilla_ bug tracking system, and
plugins for version control systems that enable interaction with
Bugzilla installations.

The only dependency is Python_ 2.7 to Pyhton_ 3.5 and bugzillatools works with
Bugzilla_ 4.0 or later where the XML-RPC feature is enabled.

.. _Bugzilla: http://www.bugzilla.org/
.. _Python: http://python.org/


Installation
============

::

  # via pip
  pip install bugzillatools         # as superuser
    -or-
  pip install bugzillatools --user  # user site-packages installation

  # from source
  python setup.py install           # as superuser
    -or-
  python setup.py install --user    # user site-packages installation

The ``bin/`` directory in your user base directory will need to appear
on the ``PATH`` if installing to user site-packages.  This directory is
system dependent; see :pep:`370`.

If installing to user site-packages, some manual moving or symlinking
of files will be required for the Bazaar plugin to be detected by
Bazaar.  :pep:`402` speaks to this shortcoming.


Components
==========

``bugzilla`` program
--------------------

Command-line application for interacting with Bugzilla servers.
The following subcommands are available:

:assign:              Assign bugs to the given user.
:block:               Show or update block list of given bugs.
:cc:                  Show or update CC List.
:comment:             List comments or file a comment on the given bugs.
:config:              Show or update configuration.
:depend:              Show or update dependencies of given bugs.
:desc:                Show the description of the given bug(s).
:dump:                Print internal representation of bug data.
:edit:                Edit the given bugs.
:fields:              List valid values for bug fields.
:help:                Show help.
:history:             Show the history of the given bugs.
:info:                Show detailed information about the given bugs.
:list:                Show a one-line summary of the given bugs.
:new:                 File a new bug.
:priority:            Set the priority on the given bugs.
:products:            List the products of a Bugzilla instance.
:search:              Search for bugs matching given criteria.
:status:              Set the status of the given bugs.
:time:                Show or adjust times and estimates for the given bugs.


``bzlib``
---------

Library providing access to Bugzilla instances through the XML-RPC
interface.  Supports bug creation, bug information and comment
retrieval, updating bug fields and appending comments to bugs.


Bazaar_ plugin
--------------

This plugin, when enabled for Bugzilla bugtrackers, marks bugs fixed on
those trackers when ``bzr commit`` is invoked with the ``--fixes`` argument.
It also adds a comment to the bug that includes the branch location, the
commit message, the list of changed files and other details about the commit.

The Bazaar_ plugin requires Bazaar 2.0 or later.

.. _Bazaar: http://bazaar.canonical.com/

``bzlib Library Usage Examples``
================================

The first step is to create a Bugzilla object that represents the Bugzilla
server you're working with

.. code:: python

    from bzlib.bugzilla import Bugzilla

    URL = "http://example.bugzilla.com"
    USERNAME = "my_username"
    password = "my_password"
    bz = Bugzilla(url=URL, username=USERNAME, password=PASSWORD)

Create a new bug

.. code:: python

    from bzlib.bug import Bug
    bz = ...  # From above
    bug = Bug(bz=bz)
    bug.data = {
        "product": "my_product",
        "component": "my_component",
        "summary": "my_summary",
        "version": "my_version",
    }

    # Send RPC call to the bugzilla server.
    bug.create()

Modify an existing bug

.. code:: python

    from bzlib.bug import Bug
    bz = ...  # From above
    BUG_ID = 1337
    bug = Bug(bz=bz, bugno_or_data=BUG_ID)
    # Modify the bug
    bug.update(whiteboard="I'm working on it, don't worry!")

    # Bug attributes are loaded lazily, so we won't get any attributes until we try
    # to access them
    bug.data  # Access the attributes

If your update has succeeded your result should have a non-empty "changes"
subsection

.. code:: python

    {'bugs': [{'alias': '',
    'changes': {'whiteboard': {'added': 'The dreaded wontfix',
        'removed': 'Sure, we'll fix it'}},
    'id': 167866,
    'last_change_time': datetime.datetime(2016, 9, 13, 23, 12, 7)}]}

If nothing was changed then you'll see

.. code:: python

    {'bugs': [{'alias': '',
    'changes': {},
    'id': 167866,
    'last_change_time': datetime.datetime(2016, 9, 13, 23, 12, 7)}]}


Configuration
=============

``.bugzillarc``
---------------

The ``bugzilla`` program looks for its configuration in
``~/.bugzillarc``, which uses ini-style configuration.

``core``
^^^^^^^^

``server``
  Name of the default server

``alias``
^^^^^^^^^

Option names are aliases; their values are the replacement.

``server.<name>``
^^^^^^^^^^^^^^^^^

Define a server.  bugzillatools supports multiple servers; the
``--server=<name>`` argument can be used to select a server.

``url``
  Base URL of the Bugzilla server (mandatory)
``user``
  Bugzilla username (optional)
``password``
  Bugzilla password (optional)
``assign_status``
  When the ``assign`` command is used, if the current status of a bug
  is in the first list, the status will be updated to the second item.
  The format is: ``<oldstatus>[,<oldstatus>]* <newstatus>``.  An
  appropriate value for the default Bugzilla workflow might be:
  ``"UNCONFIRMED,CONFIRMED IN_PROGRESS"``.
``default_product``
  If provided and if the provided string corresponds to the name of a
  product on this server, use that product as the default.  The user
  will still be prompted to confirm.


Example ``.bugzillarc``
^^^^^^^^^^^^^^^^^^^^^^^

::

  [core]
  server = example

  [server.example]
  url = http://bugzilla.example.com
  user = user@example.com
  password = sekrit

  [alias]
  fix = status --status RESOLVED --resolution FIXED
  wfm = status --status RESOLVED --resolution WORKSFORME
  confirm = status --status CONFIRMED


Bazaar plugin
-------------

To enable the Bazaar bugzillatools plugin, include following
configuration directives in either ``~/.bazaar/bazaar.conf`` (global
configuration) or ``.bzr/branch/branch.conf`` (within a branch)::

  bugzilla_<server>_bugzillatools_enable = True
  bugzilla_<server>_url = <bugzilla url>
  bugzilla_<server>_status = RESOLVED
  bugzilla_<server>_resolution = FIXED

Such a configuration assumes that a section ``[server.<server>]``
has been defined in your ``.bugzillarc``.

You can now set the status of bugs (using the status and resolution
defined in the Bazaar config) directly::

  bzr commit -m 'fix bug 123' --fixes <server>:123


License
=======

bugzillatools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.


Contributing
============

The bugzillatools source code is available at
https://github.com/rawrgulmuffins/bugzillatools.

The bugzillatools source code was available from
https://github.com/frasertweedale/bugzillatools.

Fraser Tweedale is the original author and maintainer for Bugzillatools.

Current maintainers are Brooks Kindle (brookskindle at gmail.com) and
Alex LordThorsen (AlexLordThorsen at gmail.com)

Bug reports, patches, feature requests, code review and
documentation are welcomed.

To submit a patch, please use ``git send-email`` or generate a pull
request.  Write a `well formed commit message`_.  If your patch is
nontrivial, update the copyright notice at the top of each changed
file.

.. _well formed commit message: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
