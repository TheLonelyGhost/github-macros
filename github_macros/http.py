from __future__ import print_function
import os

import requests


class GithubHttp(requests.Session):
    """
    Wrapper for a requests session object with our project-specific settings
    """

    def __init__(self, username, token, *args, **kwargs):
        super(GithubHttp, self).__init__(*args, **kwargs)

        if os.getenv('GITHUB_DOMAIN', 'github.com') in ('api.github.com', 'github.com'):
            self.base_uri = 'https://api.github.com'
        else:
            self.base_uri = 'https://{domain}/api/v3'.format(domain=os.getenv('GITHUB_DOMAIN'))
        self.auth = (username, token)
        self.headers.update({'Accept': 'application/vnd.github.loki-preview+json',
                             'Content-Type': 'application/json',
                             'User-Agent': 'David Alexander: "Too lazy... Just script it..."'})

    def prepare_request(self, request, **kwargs):
        if request.url.startswith('/'):
            # Insert our github.com api string as the base
            request.url = self.base_uri + request.url

        return super(GithubHttp, self).prepare_request(request, **kwargs)
