=======
Permit
=======
----------
gh-permit
----------

Overview
========

The objective this satisfies is to have a tool to run so repository permissions may be managed based on team membership. As users migrate roles, their memberships to certain teams may also change. This membership cascades into what repositories they are able to read/write/administer.

This command, ``gh-permit``, is intended to be entirely stateless. It does not store any data locally, instead choosing to read from the GitHub API on every invocation. Its flags are split up into 3 categories:

- `General Configuration`_
- `Targets`_
- `Rules`_

Usage
=====

.. code-block:: bash

    $ gh-permit --help
    usage: gh-permit [-h] [--version] --organization ORGANIZATION --team TEAM
                     [--permission {read,write,admin}] [--github-user GH_USER]
                     [--github-token GH_TOKEN]

    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         Prints the program version and exits
      --organization ORGANIZATION, -o ORGANIZATION
                            GitHub organization whose repositories we will alter
      --team TEAM, -t TEAM  GitHub team slug (scoped to the given organization)
                            for which to provide permissions
      --permission {read,write,admin}, -p {read,write,admin}
                            GitHub repository permissions to grant the given team
      --github-user GH_USER
      --github-token GH_TOKEN


General Configuration
=====================

These flags are as follows:

- ``--help``
  - Displays command usage documentation
- ``--version``
  - Displays version information
- ``--github-user``
  - This is the slug for your GitHub username. (Default: environent variable value ``GITHUB_USER``)
- ``--github-token``
  - This is the `GitHub API Token`_ you must have manually created. (Default: environent variable value ``GITHUB_TOKEN``)

GitHub API Token
----------------

Can be created in your `GitHub settings`_, for example, and must contain the following scopes to work properly:

- ``repo`` (Full control of private repositories)

These permissions are the bare minimum in order to see settings for public and private repositories.

.. _GitHub settings: https://github.com/settings/tokens

Targets
=======

The targets we choose will be a team by the given name (must be the slug given when @-mentioning a team), which must exist within the given organization. So if you were to give permission to the ``Ephemeral Labs`` group in the organization ``Chef-Roles``, you would provide the command line flags ``--organization chef-roles --team ephemeral-labs``. Always give the slug format you see in the URL.

This target will apply the given rules to all members of the ``Ephemeral Labs`` team (within the ``Chef-Roles`` GitHub organization) to all repositories in the ``Chef-Roles`` organization, public or private.

Rules
=====

This is just determining what permissions we want to give the target. It's any of ``read``, ``write``, or ``admin`` where

- **Read** gives permission to view the repository, fork it, and clone its contents locally. This is already applied for any user regardless of team membership if the repository is marked "Public"
- **Write** give the same permissions as **Read**, with additional capabilities to create branches, merge pull requests, create releases, and `many other capabilities`_

.. _Many other capabilities: https://help.github.com/enterprise/2.10/user/articles/repository-permission-levels-for-an-organization/

Examples
========

Give write permissions to a given team
--------------------------------------

.. code-block:: bash

    $ gh-permit --organization chef-roles --team ephemeral-labs --permission write
    TEAM: @chef-roles/ephemeral-labs (869)
    REPO: chef-roles/role_sqlserver
    REPO: chef-roles/role_maas_server
    REPO: chef-roles/role_jenkins_swarm
    REPO: chef-roles/role_windows_chef_integration
    REPO: chef-roles/role_redwood_server
    ...

