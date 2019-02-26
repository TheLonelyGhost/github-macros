import os

from github_macros.cli._base import MyParser, create_client
from github_macros.models.github import GithubOrganization
from github_macros import __version__


def get_args():
    p = MyParser()
    p.add_argument('--version', '-v', action='version',
                   help='Prints the program version and exits',
                   version='%(prog)s ' + __version__)

    p.add_argument('--organization', '-o', dest='organization', action='store', default=None, required=True,
                   help='GitHub organization whose repositories we will alter')
    p.add_argument('--team', '-t', dest='team', action='store', default=None, required=True,
                   help='GitHub team slug (scoped to the given organization) for which to provide permissions')
    p.add_argument('--permission', '-p', dest='permission', action='store', default='write', choices=['read', 'write', 'admin'],
                   help='GitHub repository permissions to grant the given team')

    p.add_argument('--github-user', dest='gh_user', action='store', default=os.getenv('GITHUB_USER'))
    p.add_argument('--github-token', dest='gh_token', action='store', default=os.getenv('GITHUB_TOKEN'))

    return p.parse_args()


def team_from_name(client, org_name, team):
    resp = client.get('/orgs/{org}/teams'.format(org=org_name))
    resp.raise_for_status()
    out = resp.json()
    for team_info in out:
        if team_info['slug'].lower() != team.lower():
            continue
        return team_info

    raise 'Team name {team} not found for organization {org}'.format(team=repr(team), org=repr(org_name))


def main():
    opts = get_args()
    client = create_client(username=opts.gh_user, token=opts.gh_token)
    client.headers.update({'Accept': 'application/vnd.github.swamp-thing-preview+json'})

    perm = {
        'read': 'pull',
        'write': 'push',
        'admin': 'admin',
    }[opts.permission]

    org_name = opts.organization
    assert org_name, 'Must provide a valid organization name in slug format'
    team = team_from_name(client, org_name, opts.team)
    assert team, 'Must provide a valid team name for the given organization'
    print('TEAM: @{org}/{team} ({_id})'.format(org=org_name, team=opts.team, _id=team['id']))

    org = GithubOrganization(client, org_name)
    for repo in org.repositories:
        resp = client.put(
            '/teams/{team_id}/repos/{repo}'.format(repo=repo.full_name, team_id=team['id']),
            json={
                'permission': perm,
            },
        )
        resp.raise_for_status()

        # NOTE: Normally a status of 201 would indicate it was written to the server, but our GHE instance is buggy that way.
        print('REPO: {repo}'.format(repo=repo.full_name))
