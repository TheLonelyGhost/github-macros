import os
import sys

from github_macros.cli._base import MyParser, create_client
from github_macros.models.github import GithubOrganization, GithubUser, GithubRepository
from github_macros import __version__


def get_args():
    defaults = {}
    p = MyParser()
    p.add_argument('--version', '-v', action='version',
                   help='Prints the program version and exits',
                   version='%(prog)s ' + __version__)

    p.add_argument('--branch', '-b', dest='branches', action='append', default=[], required=True,
                   help='Branch name in which to check branch protections')

    mapping = p.add_argument_group('Repository listing', 'Use these options for choosing '
                                   'how to select your list of repositories to check against '
                                   'for branch protection settings')
    mapping.add_argument('--repository', '-r', dest='repositories', action='append', default=[],
                         help='GitHub repository in which to check branch protections')
    mapping.add_argument('--user', '-u', dest='users', action='append', default=[],
                         help='GitHub user in which to check branch protections for all repositories')
    mapping.add_argument('--organization', '-o', dest='organizations', action='append', default=[],
                         help='GitHub organization in which to update hooks for all repositories')

    p.add_argument('--github-user', dest='gh_user', action='store', default=os.getenv('GITHUB_USER'))
    p.add_argument('--github-token', dest='gh_token', action='store', default=os.getenv('GITHUB_TOKEN'))

    # CHECKS:
    status_checks = p.add_argument_group('Commit status checks')
    status_checks.add_argument('--ci-check', dest='contexts', action='append', default=[],
                               help='Required checks (e.g., from Jenkins or other CI) in order to allow merging a PR')

    code_review = p.add_argument_group('Code review process')
    defaults['require_code_review'] = None  # If `is None`, we don't care about this setting
    code_review_opt = code_review.add_mutually_exclusive_group()
    code_review_opt.add_argument('--code-review', dest='require_code_review', action='store_true',
                                 help='Code review is necessary before merging')
    code_review_opt.add_argument('--no-code-review', dest='require_code_review', action='store_false',
                                 help='Code review is extra credit')
    defaults['auto_dismiss_review'] = None  # If `is None`, we don't care about this setting
    code_review_autodismiss = code_review.add_mutually_exclusive_group()
    code_review_autodismiss.add_argument('--auto-dismiss-review', dest='auto_dismiss_review', action='store_true',
                                         help='Pushing changes after receiving a review should automatically '
                                              'require re-review')
    code_review_autodismiss.add_argument('--no-auto-dismiss-review', dest='auto_dismiss_review', action='store_false',
                                         help='Pushing changes after receiving a review should not affect anything')
    defaults['restrict_dismiss_reviews'] = None  # If `is None`, we don't care about this setting
    code_review_dismiss = code_review.add_mutually_exclusive_group()
    code_review_dismiss.add_argument('--restrict-dismiss-review', dest='restrict_dismiss_review', action='store_true',
                                     help='No one can dismiss a code review except the one who gave it (or specified by '
                                          '--dismiss-user or --dismiss-team)')
    code_review_dismiss.add_argument('--no-restrict-dismiss-review', dest='restrict_dismiss_review', action='store_false',
                                     help='Anyone with write permissions to the repository can dismiss a code review')
    code_review.add_argument('--dismiss-user', dest='dismiss_review_users', action='append', default=[],
                             help='Ignore review dismissal restrictions for this user (allows multiple invocations of --dismiss-user)')
    code_review.add_argument('--dismiss-team', dest='dismiss_review_teams', action='append', default=[],
                             help='Ignore review dismissal restrictions for this team (allows multiple invocations of --dismiss-team)')

    defaults['except_admins'] = None  # If `is None`, we don't care about this setting
    admins = p.add_argument_group('Administrators should follow the rules too')
    admins_opts = admins.add_mutually_exclusive_group()
    admins_opts.add_argument('--enforce-for-admins', dest='except_admins', action='store_false',
                             help='Force repository/organization admins to also comply with branch protections')
    admins_opts.add_argument('--no-enforce-for-admins', dest='except_admins', action='store_true',
                             help='Allow repository/organization admins to override branch protections')

    uptodate = p.add_argument_group('Branch commits relative to upstream')
    defaults['branch_up_to_date'] = None  # If `is None`, we don't care about this setting
    uptodate_opt = uptodate.add_mutually_exclusive_group()
    uptodate_opt.add_argument('--branch-up-to-date', dest='branch_up_to_date', action='store_true',
                              help='Require (as a status check) that the branch being merged must be '
                                   'up-to-date with the upstream branch')
    uptodate_opt.add_argument('--no-branch-up-to-date', dest='branch_up_to_date', action='store_false',
                              help='Ignore if the branch being merged is not up-to-date with the upstream branch')

    # TODO: add a nice description of the rule this covers
    push = p.add_argument_group('Pushing commits directly to the branch')
    defaults['restrict_push'] = None  # If `is None`, we don't care about this setting
    push_opt = push.add_mutually_exclusive_group()
    push_opt.add_argument('--restrict-push', dest='restrict_push', action='store_true',
                          help='Disallow pushing to the specified branch (exceptions noted with --push-user '
                               'and --push-team)')
    push_opt.add_argument('--no-restrict-push', dest='restrict_push', action='store_false',
                          help='Allow pushing to the specified branch by those with write access')
    push.add_argument('--push-user', dest='allowed_push_users', action='append', default=[],
                      help='Ignore push restrictions for this user (allows multiple invocations of --push-user)')
    push.add_argument('--push-team', dest='allowed_push_teams', action='append', default=[],
                      help='Ignore push restrictions for this team (allows multiple invocations of --push-team)')

    p.set_defaults(**defaults)
    return p.parse_args()


def index_repos(client, repo_names=None, org_names=None, usernames=None):
    repositories = []
    for org_name in (org_names if org_names else []):
        # org.repositories is a lazy-loaded item, so we don't need to fetch all the info on the org
        org = GithubOrganization(client, org_name)
        repositories += org.repositories

    for username in (usernames if usernames else []):
        # user.repositories is a lazy-loaded item, so we don't need to fetch all the info on the person
        user = GithubUser(client, username)
        repositories += user.repositories

    for repo_name in (repo_names if repo_names else []):
        repositories.append(GithubRepository.fetch(client, repo_name))

    return set(repositories)


def error(repo, branch, option_name):
    msg = "ERROR:: {repo} @ {branch} => {opt}\n"
    sys.stderr.write(msg.format(repo=repo.full_name, branch=branch.name, opt=option_name))


def main():
    opt = get_args()
    client = create_client(username=opt.gh_user, token=opt.gh_token)

    # collecting repo objects for all the things
    repositories = index_repos(client=client, repo_names=opt.repositories,
                               org_names=opt.organizations, usernames=opt.users)
    all_errors = 0

    for repo in repositories:
        # print('REPO: {name}'.format(name=str(repo.full_name)))
        repo.refresh()
        repo_errors = 0

        for branch in repo.branches:
            if branch.name not in opt.branches:
                continue
            errors = 0

            if not branch.protection.enabled:
                error(repo, branch, 'Branch protection is disabled')

            errors += repo_push_checks(branch.protection, opt)
            errors += repo_code_review(branch.protection, opt)
            errors += repo_status_checks(branch.protection, opt)
            errors += repo_admin_exemptions(branch.protection, opt)

            if errors > 0:
                fix_url = '{base}/settings/branches/{branch}'.format(base=repo.url, branch=branch.name)
                msg = '===============> Fix it: {url} <==============='
                sys.stderr.write(msg.format(url=fix_url) + '\n\n')

            repo_errors += errors

        all_errors += repo_errors

    sys.exit(0 if all_errors == 0 else 1)


# RULE CHECKERS

def repo_push_checks(protection, opt):
    errors = 0
    branch = protection.branch
    repo = branch.repository

    if opt.restrict_push is None:
        return errors

    if protection.push_restrictions != opt.restrict_push:
        if protection.push_restrictions:
            error(repo, branch, 'Push restrictions are enabled')
        else:
            error(repo, branch, 'Push restrictions are disabled')
        errors += 1

    if not opt.restrict_push:
        return errors

    # TODO: Check list of users where we're overriding push restrictions
    # TODO: Check list of teams where we're overriding push restrictions

    return errors


def repo_code_review(protection, opt):
    errors = 0
    branch = protection.branch
    repo = branch.repository

    if opt.require_code_review is None:
        return errors

    if protection.required_code_review != opt.require_code_review:
        if protection.required_code_review:
            error(repo, branch, 'Mandatory code review is enabled')
        else:
            error(repo, branch, 'Mandatory code review is disabled')
        errors += 1

    if not opt.require_code_review:
        return errors

    if opt.auto_dismiss_review is not None and \
            protection.dismiss_stale_reviews != opt.auto_dismiss_review:
        if protection.dismiss_stale_reviews:
            error(repo, branch, 'Reviews are automatically dismissed when new code is pushed')
        else:
            error(repo, branch, 'Reviews remain valid when new code is pushed')
        errors += 1

    return errors


def repo_status_checks(protection, opt):
    errors = 0
    branch = protection.branch
    repo = branch.repository

    if opt.branch_up_to_date is not None:
        if protection.up_to_date != opt.branch_up_to_date:
            if protection.up_to_date:
                error(repo, branch, 'Branch must be up-to-date with upstream')
            else:
                error(repo, branch, 'Branch can be, but is not mandated to be, up-to-date with upstream')
            errors += 1

    for check in opt.contexts:
        if check not in protection.contexts:
            error(repo, branch, 'Branch is missing the "{}" check'.format(check))
            errors += 1

    return errors


def repo_admin_exemptions(protection, opt):
    errors = 0
    branch = protection.branch
    repo = branch.repository

    if opt.except_admins is not None:
        if opt.except_admins != protection.except_admins:
            if protection.except_admins:
                error(repo, branch, 'Administrators are exempt from branch protections')
            else:
                error(repo, branch, 'Administrators must also follow branch protections')
            errors += 1

    return errors


if __name__ == '__main__':
    main()
