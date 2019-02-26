=======
Refresh
=======
----------
gh-refresh
----------

Handles cloning and update local git repositories from GitHub.com (or GitHub Enterprise by setting the environment variable ``GITHUB_DOMAIN``).

One might get the following directory structure:

.. code-block::

    .
    ├── chef-roles/
    │   ├── role_jenkins_swarm/
    │   ├── role_maas_server/
    │   ├── role_sqlserver/
    │   ├── role_windows_adminsvc/
    │   └── [...]
    ├── chef-supermarket/
    │   ├── activebatch/
    │   ├── beyond_trust/
    │   ├── bginfo/
    │   ├── chef_client/
    │   ├── chef_dk/
    │   ├── chef_supermarket/
    │   ├── chocolatey/
    │   └── [...]
    └── david-alexander/
        ├── github-macros/
        ├── golint/
        ├── inspec-patching_checks/
        ├── powershell-patches/
        ├── pre-commit-go-hooks/
        ├── pre-commit-hooks/
        └── scripts/

Overview
========

The objective it satisfies is to fill in any new repositories that show up in the organizations or user accounts configured. If the specified repository does not exist, it clones it with ``git clone`` and the SSH syntax of the clone URL (setup your private key!). Otherwise it runs ``git fetch origin``.

This command, ``gh-refresh``, is intended to be entirely stateless. It does not store any data locally (except the repositories you intend to mirror from GitHub), instead choosing to read from the GitHub API on every invocation.

Usage
=====

.. code-block:: bash

    $ gh-refresh --help
    usage: gh-refresh [-h] [--version] [--user USERS]
                      [--organization ORGANIZATIONS] [--base-dir BASE_DIRECTORY]
                      [--github-user GH_USER] [--github-token GH_TOKEN]
                      [--dry-run]
    
    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         Prints the program version and exits
      --user USERS, -u USERS
                            Github user from which to clone/update all
                            repositories
      --organization ORGANIZATIONS, -o ORGANIZATIONS
                            Github organization from which to clone/update all
                            repositories
      --base-dir BASE_DIRECTORY
                            The directory where repositories will be cloned in a
                            Github-like directory structure
      --github-user GH_USER
      --github-token GH_TOKEN
      --dry-run

If you don't want to embed your GitHub user credentials, ``--github-user`` defaults to the environment variable ``GITHUB_USER`` and ``--github-token`` defaults to ``GITHUB_TOKEN``.

Examples
========

.. TODO:  Insert GIF of asciicast

Clone or update from list of GitHub organizations
-------------------------------------------------

.. code-block:: bash

    $ gh-refresh --organization='chef-supermarket' --organization='chef-roles' --organization='chef-inspec'

Clone or update from list of other GitHub user accounts
-------------------------------------------------------

.. code-block:: bash

    $ gh-refresh --user='david-alexander' --user='bmichel'

Persisted personal settings
---------------------------

Setup in shell init file:

.. code-block:: bash

    # File: ~/.bashrc, ~/.bash_profile, or ~/.zshrc (depending on your platform and chosen shell)

    alias gh-refresh='command gh-refresh -o chef-supermarket -o chef-roles --base-dir ~/workspace'

Then run without arguments:

.. code-block:: bash

    $ gh-refresh
