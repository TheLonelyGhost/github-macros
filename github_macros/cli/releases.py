import os
import re

from github_macros.cli._base import MyParser, create_client
from github_macros import __version__


def gh_client():
    return create_client(os.getenv('GITHUB_USER'), os.getenv('GITHUB_TOKEN'))


def get_args():
    p = MyParser()
    p.add_argument('--version', '-v', action='version',
                   help='Prints the program version and exits',
                   version='%(prog)s ' + __version__)

    p.add_argument('--github-user', dest='gh_user',
                   action='store', default=os.getenv('GITHUB_USER'))
    p.add_argument('--github-token', dest='gh_token',
                   action='store', default=os.getenv('GITHUB_TOKEN'))

    p.add_argument('--prefix', dest='pfx', action='store', default='v',
                   help='Version prefix applied to semver tags')
    p.add_argument('--pattern', dest='version_pattern', action='store', default='',
                   help='A python-based regular expression for what pattern indicates a version tag')

    p.add_argument('--latest', dest='latest', action='store_true', default=False,
                   help='Grab only the latest release')

    p.add_argument('repo', metavar='REPO', action='store', help='The target repository for which to find the latest version (e.g., "postmodern/chruby")')

    return p.parse_args()


def get_releases(repo, client, pattern=r'^v\d+\.\d+\.\d+'):
    response = client.get('/repos/{}/releases'.format(repo), params={'per_page': 999})
    response.raise_for_status()
    version_pattern = re.compile(pattern)  # Only version tags
    unstable_version_pattern = re.compile(r'\d-?(rc\d*|a(lpha)?\d*|b(eta)?\d*)$')

    def is_final_release(release):
        if release['draft']:
            return False
        if release['prerelease']:
            return False
        if unstable_version_pattern.search(release['tag_name']):
            return False

        return True

    def is_version_tag(release):
        return bool(version_pattern.search(release['tag_name']))

    return sorted(
        filter(
            lambda r: is_version_tag(r) and is_final_release(r),
            response.json() or [],
        ),
        key=lambda release: release['tag_name'],
    )


def show_release_info(release, client):
    response = client.get(release['assets_url'], params={'per_page': 999})
    response.raise_for_status()
    assets = response.json()

    for asset in assets:
        print('{tag}\t{name}\t{url}'.format(tag=release['tag_name'], name=asset['name'], url=asset['browser_download_url']))


def main():
    opts = get_args()
    client = create_client(username=opts.gh_user, token=opts.gh_token)
    if opts.version_pattern:
        version_pattern = opts.version_pattern
    else:
        version_pattern = '^{}'.format(opts.pfx) + r'\d+\.\d+\.\d+'

    if opts.latest:
        releases = get_releases(opts.repo, client, pattern=version_pattern)
        if len(releases) > 0:
            show_release_info(releases[-1], client)
    else:
        for release in get_releases(opts.repo, client, pattern=version_pattern):
            show_release_info(release, client)


if __name__ == '__main__':
    main()
