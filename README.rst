bugzillatools consists of the ``bugzilla`` CLI program and a Python
library for interacting with the Bugzilla_ bug tracking system, and
plugins for version control systems that enable interaction with
Bugzilla installations.

The only dependency is Python_ 2.7 and bugzillatools works with
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

The bugzillatools source code is available from
https://github.com/frasertweedale/bugzillatools.

Bug reports, patches, feature requests, code review and
documentation are welcomed.

To submit a patch, please use ``git send-email`` or generate a pull
request.  Write a `well formed commit message`_.  If your patch is
nontrivial, update the copyright notice at the top of each changed
file.

.. _well formed commit message: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
