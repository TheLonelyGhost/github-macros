import os

from github_macros.cli._base import MyParser, create_client
from github_macros.models.github import GithubOrganization, GithubUser
from github_macros import __version__

from sh.contrib import git as git_cmd
import sh


def git(*args, **kwargs):
    exc = None
    for attempt in range(3):
        try:
            return git_cmd(*args, **kwargs)
        except sh.ErrorReturnCode_128 as e:
            exc = e
            continue
    if exc:
        raise exc


def git_ref_resolve(repo, ref):
    path = os.path.join(repo.owner.name, repo.name)
    try:
        return git('-C', path, 'rev-parse', '--abbrev-ref', ref).strip()
    except sh.ErrorReturnCode:
        return None


def clone(repo, fake=False, clobber=False):
    """
    """
    path = os.path.join(repo.owner.name, repo.name)

    if os.path.exists(path):
        print(' REPO: Updating {repo}'.format(repo=repo.full_name))
        if fake:
            return
        git('-C', path, 'fetch', 'origin')
        if not clobber:
            return

        branch_name = git_ref_resolve(repo, 'HEAD')

        if branch_name == 'master':
            git('-C', path, 'reset', '--hard', 'origin/master')
        elif branch_name:
            git('-C', path, 'branch', '-f', 'master', 'origin/master')
        elif git_ref_resolve(repo, 'origin/master'):
            git('-C', path, 'pull', 'origin', 'master')

    else:
        os.makedirs(path)
        print(' REPO: Cloning {repo}'.format(repo=repo.full_name))
        if fake:
            return
        git('clone', repo.clone_url, path)


def get_args():
    p = MyParser()
    p.add_argument('--version', '-v', action='version',
                   help='Prints the program version and exits',
                   version='%(prog)s ' + __version__)

    p.add_argument('--user', '-u', dest='users', action='append', default=[os.getenv('GITHUB_USER')] if os.getenv('GITHUB_USER') else [],
                   help='GitHub user from which to clone/update all repositories')
    p.add_argument('--organization', '-o', dest='organizations', action='append', default=[],
                   help='GitHub organization from which to clone/update all repositories')
    p.add_argument('--base-dir', dest='base_directory', action='store', default=os.getcwd(),
                   help='The directory where repositories will be cloned in a Github-like directory structure')

    p.add_argument('--github-user', dest='gh_user', action='store', default=os.getenv('GITHUB_USER'))
    p.add_argument('--github-token', dest='gh_token', action='store', default=os.getenv('GITHUB_TOKEN'))

    p.add_argument('--dry-run', dest='dry_run', action='store_true', default=False)

    p.add_argument('--clobber', '-F', dest='clobber', action='store_true', default=False,
                   help='Overwrite existing working copy for each repository')

    return p.parse_args()


def main():
    opts = get_args()
    os.chdir(opts.base_directory)
    client = create_client(username=opts.gh_user, token=opts.gh_token)

    for org_name in set(opts.organizations):
        # org.repositories is a lazy-loaded item, so we don't need to fetch all the info on the org
        org = GithubOrganization(client, org_name)
        managed_directories = set([])

        print('  ORG: {org}'.format(org=org.name))
        for repo in org.repositories:
            managed_directories.add(os.path.join(repo.owner.name, repo.name))
            clone(repo, fake=opts.dry_run, clobber=opts.clobber)

        # list directories in {org.name} directory
        for directory_name in os.listdir(org.name):
            full_path = os.path.join(org.name, directory_name)
            if not os.path.isdir(full_path):
                continue
            if full_path in managed_directories:
                continue

            print('EXTRA: {directory}'.format(directory=full_path))

    for username in set(opts.users):
        # user.repositories is a lazy-loaded item, so we don't need to fetch all the info on the person
        user = GithubUser(client, username)
        managed_directories = set([])

        print(' USER: {user}'.format(user=user.name))
        for repo in user.repositories:
            managed_directories.add(os.path.join(repo.owner.name, repo.name))
            clone(repo, fake=opts.dry_run, clobber=opts.clobber)

        # list directories in {user.name} directory
        for directory_name in os.listdir(user.name):
            full_path = os.path.join(user.name, directory_name)
            if not os.path.isdir(full_path):
                continue
            if full_path in managed_directories:
                continue

            print('EXTRA: {directory}'.format(directory=full_path))


if __name__ == '__main__':
    main()
