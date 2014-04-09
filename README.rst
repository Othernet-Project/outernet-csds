===============================================
Outernet Content Selection and Discovery System
===============================================

This repository contains the Outernet Content Selection and Discovery System.
It is currently is concept stage, where we are exploring the implementation and
trying to get some real-life feedback on how the CSDS should work.

Repository layout
=================

The repository contains the following directories::

    \
    ├───app         # Package that ties together all web-based components
    ├───cds         # Content Discovery Subsystem
    ├───css         # Content Selection Subsystem
    ├───ra          # Request Adaptors
    ├───rh          # Request Hub
    ├───rqm         # Request Query Manager
    ├───migrations  # Data migrations
    ├───src         # Compiled static assets (Compass, LiveScript)
    ├───static      # Static assets (JavaScript, CSS, images)
    ├───templates   # HTML and plain-text templates used by web-based UI
    ├───tests       # Unit tests
    └───tools       # Configuration and build tools

While developing, the tools may create various directories not listed above
(such as ``vendor`` directory that contains the application's Python 
dependencies).

Branches
========

The repository is using the Git Flow layout, and development is on ``develop``
branch. The master branch is always going to be in synch with most recently
deployed production code (sans the production configuration settings).

Please read more about `Git Flow`_ before contributing to this code base.

Package contents
================

Here is a brief description of various packages' and files' contents.

Web Application (app)
---------------------

This package contains the glue code and miscellaneous components that don't fit
in any other package. The package's ``app.main`` module implements the ``app``
object which is used as the main entry point for Google AppEngine requests.

Configuration settings for different components is found in the ``app.conf``
module. This module is used to configure components such as adaptors, which
require runtime configuration that cannot be hard-wired in their own modules
for maintainability and security reasons.

Request adaptors (ra)
---------------------

The request adaptors are subclasses of the ``rh.adaptors.Adaptor`` class. They
implement the ``get_requests()`` method to fetch requests (usually in a cron
job). 

Currently, the only working example is Outernet Facebook page adaptor which you
can find in ``ra.outernet_facebook`` module. The module also implements its own
Cron job handler.

Cron job handlers (cron.yaml)
-----------------------------

Each request adaptor can perform its own harvesting in a cron job. To
standardize the way cron jobs are handled, a
``rh.requests.CronJobHandlerMixin`` mixin is provided. It's a simple class
meant to be used with FlaskWarts_ ``Request`` class. This is not a requirement,
though. If the handler does not use the ``Request`` class, it does not need ot
use the ``CronJobHandlerMixin``.

Request hub (rh)
----------------

Request hub currently has no web-based interface. It will house the RH public
API once we know what it needs to do, but for now it simply houses the code
used directly by other components, and the database schema definitions.

The ``rh`` package contains interfaces for working with requests and persisting
various pieces of data.

Content discovery subsystem (cds)
---------------------------------

The ``csd`` package contains the web-based interface for the content discovery
subsystem which allows users to see a listing of requests that have not yet
been fulfilled by the Outernet, and submit content suggestions.

Content selection subsystem (css)
---------------------------------

The ``css`` package (which has nothing to do with cascading stylesheets)
contains the web-based interface for voting.

Developing
==========

To develop this application, you will need Python, latest `Google AppEngine 
SDK`_, Ruby, Ruby Gems, and Compass. You will also need to install a Python
package called ``zoro`` (note that it's called 'zoro', not 'zorro').

Create a virtualenv for this application, and then, once the environment is
activated, run the following command from the repository root::

    zorofile check

This will perform the preflight check to make sure all required dependencies
are installed. The check isn't foolproof, and it will ignore errors raied by
some package managers, so please make sure you read the output carefully.

Run ``zorofile -l`` or ``zorofile --list`` to see all build targets defined in
the zorofile. The two you will use most often are ``test`` (run unit tests in
watch mode) and ``dev`` (start the development server).

Contributing code
=================

TODO

Reporting issues
================

Please report any issues to the `GitHub issue tracker`_.

=======
License
=======

Outernet CSDS
Copyright (C) 2014, Outernet Inc.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see http://www.gnu.org/licenses/.

.. _Git Flow: http://nvie.com/posts/a-successful-git-branching-model/
.. _FlaskWarts: https://pypi.python.org/pypi/FlaskWarts/0.1a7
.. _Google AppEngine SDK: https://developers.google.com/appengine/downloads
.. _GitHub issue tracker: https://github.com/Outernet-Project/outernet-csds/issues
