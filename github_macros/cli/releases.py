import logging
import os
import re
import sys

from github_macros.cli._base import MyParser, create_client
from github_macros import __version__


logging.basicConfig()
log = logging.getLogger(__name__)


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

    p.add_argument('--log-level', dest='log_level', action='store', default='NOTSET',
                   help='Set the log level, for debugging purposes')

    p.add_argument('--source', dest='include_source', action='store_true', default=False,
                   help='Include source code archives (*.tar.gz and *.zip) as a download option')

    p.add_argument('--alpha', dest='allowed', action='store_const', const=['alpha', 'beta', 'rc'],
                   help='Matches alpha releases')
    p.add_argument('--beta', dest='allowed', action='store_const', const=['beta', 'rc'],
                   help='Matches beta releases')
    p.add_argument('--rc', dest='allowed', action='store_const', const=['rc'],
                   help='Matches Release Candidate ("-rc") releases')

    p.add_argument('--latest', dest='latest', action='store_true', default=False,
                   help='Grab only the latest release')

    p.add_argument('repo', metavar='REPO', action='store', help='The target repository for which to find the latest version (e.g., "postmodern/chruby")')

    p.set_defaults(allowed=[])
    return p.parse_args()


def get_releases(repo, client, pattern=r'^v\d+\.\d+\.\d+', versions_allowed=[]):
    response = client.get('/repos/{}/releases'.format(repo), params={'per_page': 999})
    response.raise_for_status()
    version_pattern = re.compile(pattern)  # Only version tags

    rc_version_pattern = re.compile(r'\d-?rc\d*$')
    beta_version_pattern = re.compile(r'\d-?b(eta)?\d*$')
    alpha_version_pattern = re.compile(r'\d-?a(lpha)?\d*$')

    def filter_criteria(release):
        if not version_pattern.search(release['tag_name']):
            log.debug('SKIP: {} does not match the given pattern {}'.format(repr(release['tag_name']), repr(pattern)))
            return False

        if release['draft']:
            log.debug('SKIP: {} is marked as a draft release'.format(repr(release['tag_name'])))
            return False

        if len(versions_allowed) == 0 and release['prerelease']:
            log.debug('SKIP: {} is marked as a pre-release'.format(repr(release['tag_name'])))
            return False

        if 'alpha' not in versions_allowed and alpha_version_pattern.search(release['tag_name']):
            log.debug('SKIP: {} was detected to be an alpha release'.format(repr(release['tag_name'])))
            return False
        if 'beta' not in versions_allowed and beta_version_pattern.search(release['tag_name']):
            log.debug('SKIP: {} was detected to be a beta release'.format(repr(release['tag_name'])))
            return False
        if 'rc' not in versions_allowed and rc_version_pattern.search(release['tag_name']):
            log.debug('SKIP: {} was detected to be a release candidate'.format(repr(release['tag_name'])))
            return False

        return True

    def sort_criteria(release):
        return release['tag_name']

    out = list(response.json() or [])
    log.debug('All: {}'.format(repr([sort_criteria(x) for x in out])))
    out = list(filter(filter_criteria, out))
    log.debug('Filtered: {}'.format(repr([sort_criteria(x) for x in out])))
    out = list(sorted(out, key=sort_criteria))
    log.debug('Sorted: {}'.format(repr([sort_criteria(x) for x in out])))

    return out


def show_release_info(release, client, include_source=False):
    log.info('Release: {}'.format(release['tag_name']))
    assets = release['assets']

    if include_source:
        sys.stdout.write('{tag}\t{name}\t{url}\n'.format(tag=release['tag_name'], name='source.tar.gz', url=release['tarball_url']))
        sys.stdout.write('{tag}\t{name}\t{url}\n'.format(tag=release['tag_name'], name='source.zip', url=release['zipball_url']))
    elif len(assets) == 0:
        # log.info('No assets found for {}'.format(release['tag_name']))
        sys.stderr.write('No uploaded assets found for {version}\n'.format(version=release['tag_name']))

    for asset in assets:
        sys.stdout.write('{tag}\t{name}\t{url}\n'.format(tag=release['tag_name'], name=asset['name'], url=asset['browser_download_url']))


def set_log_level(level):
    if level.startswith('debug'):
        log.setLevel(logging.DEBUG)
    elif level.startswith('info'):
        log.setLevel(logging.INFO)
    elif level.startswith('warn'):
        log.setLevel(logging.WARNING)
    elif level.startswith('error'):
        log.setLevel(logging.ERROR)
    elif level.startswith('crit'):
        log.setLevel(logging.CRITICAL)
    else:
        log.setLevel(logging.NOTSET)


def main():
    opts = get_args()
    set_log_level(opts.log_level.lower())

    client = create_client(username=opts.gh_user, token=opts.gh_token)
    if opts.version_pattern:
        version_pattern = opts.version_pattern
    else:
        version_pattern = '^{}'.format(opts.pfx) + r'\d+\.\d+\.\d+'

    if opts.latest:
        releases = get_releases(opts.repo, client, pattern=version_pattern, versions_allowed=opts.allowed)
        if len(releases) > 0:
            show_release_info(releases[-1], client, include_source=opts.include_source)
    else:
        for release in get_releases(opts.repo, client, pattern=version_pattern, versions_allowed=opts.allowed):
            show_release_info(release, client, include_source=opts.include_source)


if __name__ == '__main__':
    main()
