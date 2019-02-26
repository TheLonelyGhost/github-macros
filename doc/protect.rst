=======
Protect
=======
----------
gh-protect
----------

Overview
========

The objective this satisfies is to have a tool to run periodically, indicating if any repository deviates from the expected norm. It can be run across one branch or multiple, and multiplied across one or more repositories.

This command, ``gh-protect``, is intended to be entirely stateless. It does not store any data locally, instead choosing to read from the GitHub API on every invocation. Its flags are split up into 3 categories:

- `General Configuration`_
- `Targets`_
- `Rules`_

Usage
=====

.. code-block:: bash

    $ gh-protect --help
    usage: gh-protect [-h] [--version] --branch BRANCHES
                      [--repository REPOSITORIES] [--user USERS]
                      [--organization ORGANIZATIONS] [--github-user GH_USER]
                      [--github-token GH_TOKEN] [--code-review | --no-code-review]
                      [--auto-dismiss-review | --no-auto-dismiss-review]
                      [--restrict-dismiss-review | --no-restrict-dismiss-review]
                      [--dismiss-user DISMISS_REVIEW_USERS]
                      [--dismiss-team DISMISS_REVIEW_TEAMS]
                      [--enforce-for-admins | --no-enforce-for-admins]
                      [--branch-up-to-date | --no-branch-up-to-date]
                      [--restrict-push | --no-restrict-push]
                      [--push-user ALLOWED_PUSH_USERS]
                      [--push-team ALLOWED_PUSH_TEAMS]

    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         Prints the program version and exits
      --branch BRANCHES, -b BRANCHES
                            Branch name in which to check branch protections
      --github-user GH_USER
      --github-token GH_TOKEN

    Repository listing:
      Use these options for choosing how to select your list of repositories to
      check against for branch protection settings

      --repository REPOSITORIES, -r REPOSITORIES
                            Github repository in which to check branch protections
      --user USERS, -u USERS
                            Github user in which to check branch protections for
                            all repositories
      --organization ORGANIZATIONS, -o ORGANIZATIONS
                            Github organization in which to update hooks for all
                            repositories

    Code review process:
      --code-review         Code review is necessary before merging
      --no-code-review      Code review is extra credit
      --auto-dismiss-review
                            Pushing changes after receiving a review should
                            automatically require re-review
      --no-auto-dismiss-review
                            Pushing changes after receiving a review should not
                            affect anything
      --restrict-dismiss-review
                            No one can dismiss a code review except the one who
                            gave it (or specified by --dismiss-user or --dismiss-
                            team)
      --no-restrict-dismiss-review
                            Anyone with write permissions to the repository can
                            dismiss a code review
      --dismiss-user DISMISS_REVIEW_USERS
                            Ignore review dismissal restrictions for this user
                            (allows multiple invocations of --dismiss-user)
      --dismiss-team DISMISS_REVIEW_TEAMS
                            Ignore review dismissal restrictions for this team
                            (allows multiple invocations of --dismiss-team)

    Administrators should follow the rules too:
      --enforce-for-admins  Force repository/organization admins to also comply
                            with branch protections
      --no-enforce-for-admins
                            Allow repository/organization admins to override
                            branch protections

    Branch commits relative to upstream:
      --branch-up-to-date   Require (as a status check) that the branch being
                            merged must be up-to-date with the upstream branch
      --no-branch-up-to-date
                            Ignore if the branch being merged is not up-to-date
                            with the upstream branch

    Pushing commits directly to the branch:
      --restrict-push       Disallow pushing to the specified branch (exceptions
                            noted with --push-user and --push-team)
      --no-restrict-push    Allow pushing to the specified branch by those with
                            write access
      --push-user ALLOWED_PUSH_USERS
                            Ignore push restrictions for this user (allows
                            multiple invocations of --push-user)
      --push-team ALLOWED_PUSH_TEAMS
                            Ignore push restrictions for this team (allows
                            multiple invocations of --push-team)

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

- ``read:org`` (Read org and team membership)

These permissions are the bare minimum in order to see settings for public and private repositories.

.. _GitHub settings: https://github.com/settings/tokens

Targets
=======

The first step is to determine the target branch, with one or more invocations of ``--branch <branch_name>``.

Next we determine a list of repositories in which to apply the rules (specified later). We can do that on a one-by-one basis with the ``--repository <repo>`` flag or on a massive basis with the ``--user <username>`` or ``--organization <org>`` flags.

Next is figuring out how far it will spread. Do you want it to check just one repository ``--repository <repo_slug>`` or all repositories for an organization ``--organization <org>``? Maybe all repositories under a certain user account ``--user <username>``? Multiple of any of these flags will only add to the list of repositories it checks.

Rules
=====

Anytime we set a flag related to a rule, it means we care about what that rule is on the target repository's branch protections. If it's not specified, it is assumed, protected or not, that whatever currently is set is perfectly fine.

For example, if I specify ``--code-review``, it will check that my branch enforces an approval review of my pull request before merging to any of the target branches, printing an error message if that is not the case. If, on the other hand, I specify ``--no-code-review``, it will error out if code reviews are enforced. When neither ``--code-review`` or ``--no-code-review`` are specified, anything goes when it comes to that setting.

Mandatory Code Review
---------------------

This is governed by the flags ``--code-review`` and ``--no-code-review`` respectively. If the ``--code-review`` flag is given, it asserts that a contributor with write access to the repository must first get the an approval on the pull request in order to merge it into the target branch (or any of the target branches, if multiple given). The opposite holds true with ``--no-code-review``, mandating that a contributor is *not* restricted by needing any form of code review in order to merge their pull request.


Examples
========


Enforce full peer review and CI for chef-supermarket repositories
-----------------------------------------------------------------

.. code-block:: bash

    $ gh-protect --branch='master' --organization='chef-supermarket' --code-review --auto-dismiss-review --restrict-dismiss-review --enforce-for-admins --branch-up-to-date --restrict-push
    ERROR:: chef-supermarket/dev_tools @ master => Administrators are exempt from branch protections
    ===============> Fix it: https://github.com/chef-supermarket/dev_tools/settings/branches/master <===============
    
    ERROR:: chef-supermarket/powercli @ master => Administrators are exempt from branch protections
    ===============> Fix it: https://github.com/chef-supermarket/powercli/settings/branches/master <===============

