import argparse
import sys

from github_macros.http import GithubHttp


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('ERROR: %s\n\n' % message)
        self.print_help()
        sys.exit(2)


def create_client(username, token):
    if not username:
        raise KeyError('Requires Github username to be given via GITHUB_USER variable or command line flag')
    if not token:
        raise KeyError('Requires Github personal access token to be given via GITHUB_TOKEN variable or command line flag')

    return GithubHttp(username=username, token=token)
