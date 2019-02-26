=============
GitHub Macros
=============

A toolchain for interacting with GitHub via the command line. Contrary to what other tools might do (*cough cough* `hub`_), this does not proxy all of your ``git`` commands. It is intended to be entirely separate from ``git`` itself, only using it as an automation tool when necessary.

Commands
========

- gh-refresh_ -- Mirror GitHub repositories
- gh-protect_ -- Check branch protection of repositories
- gh-permit_ -- Grant collaborator access for repositories
- gh-releases_ -- List asset download URLs of a repository's release

Installation
============

It is *highly* recommended that you install pipsi_ for *any* Python command line application. It sandboxes the command's dependencies and, in case you have a Python version switcher such as ``pyenv``, links to a specific version of Python regardless of what you're currently using.

.. code-block:: bash

    $ pipsi install github_macros

If you receive an error on this, perhaps the package was already installed

.. code-block:: bash

    $ pipsi upgrade github_macros

GitHub Token
------------

To use these tools, we make use of the GitHub APIs, which are only (reliably) accessible with a `Personal Access Token`_. The scopes granted to this token are listed with each command's documentation.

Compatibility
-------------

This toolset was designed for use with `github.com`, or with GitHub Enterprise 2.10 or above by setting the environment variable ``GITHUB_DOMAIN``.

Uninstallation
==============

In case there's ever any issue where you want to completely remove this application, here's how you do it:

.. code-block:: bash

    $ pipsi uninstall github_macros

The final step--and this is *super important*--is to weep gently into your arms for the lost productivity.

.. _hub: https://hub.github.com/
.. _gh-protect: /doc/protect.rst
.. _gh-refresh: /doc/refresh.rst
.. _gh-permit: /doc/permit.rst
.. _gh-releases: /doc/releases.rst
.. _pipsi: https://github.com/mitsuhiko/pipsi
.. _Personal Access Token: https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line
