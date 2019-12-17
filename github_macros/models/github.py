"""
A read-only set of models in the active record pattern, reading from GitHub's API
and transforming it into a pythonic set of objects.
"""

from typing import Any, Dict, List, Optional, Union
from abc import ABC as AbstractBaseClass, abstractmethod

from github_macros.http import GithubHttp
from github_macros.common import cached_property

import dateutil.parser
from datetime import datetime


def parse_iso8601(stamp):
    return dateutil.parser.parse(stamp)


def debug(msg):
    # print("=================> DEBUG: {}".format(msg))
    pass


class BaseGithubSerializer(AbstractBaseClass):
    ALLOWED_MAPS: List[str] = []  # To be overridden in subclasses

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, client: GithubHttp, name: str, **kwargs):
        """
        param:: client: An instance of `github_macros.http.GithubHttp`
        param:: name: The organization slug of the target
        """
        self.http = client
        self.name = name
        self._set_props(**kwargs)

    def _set_props(self, **kwargs):
        for attr in self.ALLOWED_MAPS:
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])

        # Datetime serialization:
        for stamp_attr in ['created_at', 'updated_at', 'pushed_at']:
            if stamp_attr in kwargs:
                setattr(self, stamp_attr, parse_iso8601(kwargs[stamp_attr]))

    @abstractmethod
    def refresh(self):
        """
        Refreshes data from Github
        """
        pass

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serializes self into JSON compatible with Github's API
        """
        return {}

    def __hash__(self):
        return hash(str(self.name))

    def __eq__(self, other) -> bool:
        if '__hash__' not in dir(other):
            # All subclasses of this have a definition for `__hash__()`
            return False

        if not isinstance(other, type(self)) and not isinstance(self, type(other)):
            # one is not an instance (or sub-class) of the other
            return False

        return self.__hash__() == other.__hash__()


class GithubOrganization(BaseGithubSerializer):
    ALLOWED_MAPS = ['login', 'id', 'company', 'blog', 'location', 'email',
                    'has_organization_projects', 'has_repository_projects',
                    'public_repos', 'public_gists', 'followers', 'following',
                    'total_private_repos', 'owned_private_repos', 'private_gists',
                    'collaborators', 'description', 'default_repository_permission',
                    'members_can_create_repositories', 'billing_email']

    id: str
    login: str
    display_name: str
    description: str
    company: str
    blog: str
    location: str
    email: str
    billing_email: str
    has_organization_projects: bool = False
    has_repository_projects: bool = False
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    total_private_repos: int = 0
    owned_private_repos: int = 0
    private_gists: int = 0
    collaborators: int = 0
    default_repository_permission: str = 'read'
    members_can_create_repositories: bool = False

    def _set_props(self, **kwargs):
        if 'login' in kwargs:
            self.name = kwargs['login']
        if 'name' in kwargs:
            self.display_name = kwargs['name']
        super(GithubOrganization, self)._set_props(**kwargs)

    @classmethod
    def fetch(cls, client: GithubHttp, name: str) -> 'GithubOrganization':
        """
        Easy, user-facing way to retrieve a record from the REST API
        """
        out = cls(client, name)
        out.refresh()
        return out

    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError()

    def refresh(self):
        resp = self.http.get('/orgs/{org}'.format(org=self.name), params={'per_page': 999})
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)

        # clear cache to re-fetch sub-resources
        if 'repositories' in self.__dict__:
            del self.__dict__['repositories']
        if 'members' in self.__dict__:
            del self.__dict__['members']

    @cached_property
    def repositories(self) -> List['GithubRepository']:
        resp = self.http.get('/orgs/{org}/repos'.format(org=self.name), params={'per_page': 999})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        out = resp.json()

        return [GithubRepository.deserialize(self.http, repo) for repo in out]

    @cached_property
    def members(self) -> List['GithubUser']:
        resp = self.http.get('/orgs/{org}/members'.format(org=self.name), params={'per_page': 999})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        out = resp.json()

        return [GithubUser.deserialize(self.http, user) for user in out]

    def __str__(self):
        return 'Github Organization ({o})'.format(o=str(self.name))


class GithubUser(BaseGithubSerializer):
    # 1-to-1 mappings between JSON and object attributes:
    ALLOWED_MAPS = ['id', 'login', 'site_admin', 'company', 'email', 'location', 'bio']

    id: str
    login: str
    display_name: str
    site_admin = False
    company: str
    email: str
    location: str
    bio: str

    def refresh(self):
        resp = self.http.get('/users/{u}'.format(u=self.name), params={'per_page': 999})
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)

        # clear cache to re-fetch sub-resources
        if 'repositories' in self.__dict__:
            del self.__dict__['repositories']

    def _set_props(self, **kwargs):
        # Weird mappings to be consistent with other models, where `name` is the unique slug,
        # but here `name` is the person's first and last name (e.g., "David Alexander" not the
        # username)
        if 'login' in kwargs:
            self.name = kwargs['login']
        if 'name' in kwargs:
            self.display_name = kwargs['name']

        super(GithubUser, self)._set_props(**kwargs)

    @classmethod
    def fetch(cls, client: GithubHttp, name: str) -> 'GithubUser':
        """
        Easy, user-facing way to retrieve a record from the REST API
        """
        out = cls(client, name)
        out.refresh()
        return out

    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, client: GithubHttp, obj: Dict[str, Any]) -> 'GithubUser':
        """
        Deserializes Github's JSON payload into a new instance of self
        """
        name = str(obj.get('name'))
        if 'name' in obj:
            del obj['name']

        return cls(client=client, name=name, **obj)

    @cached_property
    def repositories(self) -> List['GithubRepository']:
        resp = self.http.get('/users/{u}/repos'.format(u=self.name), params={'per_page': 999})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        out = resp.json()

        return [GithubRepository.deserialize(self.http, repo) for repo in out]

    def __str__(self) -> str:
        return 'Github User ({u})'.format(u=str(self.name))


class GithubRepository(BaseGithubSerializer):
    # 1-to-1 mappings between JSON and object attributes:
    ALLOWED_MAPS = ['homepage', 'language', 'watchers', 'default_branch', 'full_name',
                    'fork', 'forks', 'stars', 'issues', 'open_issues', 'description',
                    'permissions']

    description: str
    full_name: str
    owner: Union[GithubOrganization, GithubUser]
    homepage: str
    language: str
    url: str
    private: bool = False
    fork: bool = False
    stars: int = 0
    watchers: int = 0
    forks: int = 0
    issues: int = 0
    open_issues: int = 0
    clone_url: str
    pushed_at: Optional[datetime]

    def __init__(self, client, full_name, **kwargs):
        self.permissions = {}
        self.full_name = full_name
        name = full_name.split('/').pop()
        if 'name' in kwargs:
            del kwargs['name']
        super(GithubRepository, self).__init__(client, name, **kwargs)

    def refresh(self):
        if not self.full_name:
            raise Exception('Requires that the `full_name` attribute be set')
        resp = self.http.get('/repos/{r}'.format(r=self.full_name), params={'per_page': 999})
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)

    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def fetch(cls, client: GithubHttp, name: str) -> 'GithubRepository':
        """
        Easy, user-facing way to retrieve a record from the REST API
        """
        out = cls(client, name)
        out.refresh()
        return out

    @classmethod
    def deserialize(cls, client: GithubHttp, obj: Dict[str, Any]) -> 'GithubRepository':
        """
        Deserializes Github's JSON payload into a new instance of self
        """
        name = str(obj.get('name'))
        if 'name' in obj:
            del obj['name']

        return cls(client=client, name=name, **obj)

    def _set_props(self, **kwargs):
        if 'owner' in kwargs:
            owner = kwargs['owner'] or {}
            if 'type' not in owner:
                raise ValueError('Unable to determine the type for repo owner')
            elif str(owner['type']).lower() == 'organization':
                self.owner = GithubOrganization.deserialize(
                    client=self.http, obj=kwargs['owner'] or {}
                )
                pass
            elif str(owner['type']).lower() == 'user':
                self.owner = GithubUser.deserialize(
                    client=self.http, obj=kwargs['owner'] or {}
                )
            else:
                raise ValueError('Unable to determine the right model to use '
                                 'for deserializing type {t}'.format(
                                     t=kwargs['owner']['type']))

        self.clone_url = ''
        if 'ssh_url' in kwargs:
            self.clone_url = kwargs['ssh_url']
        elif 'git_url' in kwargs:
            self.clone_url = kwargs['git_url']
        elif 'clone_url' in kwargs:
            self.clone_url = kwargs['clone_url']

        self.url = ''
        if 'html_url' in kwargs:
            self.url = kwargs['html_url']

        super(GithubRepository, self)._set_props(**kwargs)

    def __str__(self):
        return 'Github Repository ({o})'.format(o=str(self.full_name))

    def __hash__(self):
        return hash(self.full_name)

    @cached_property
    def branches(self) -> List['GithubBranch']:
        if not self.full_name:
            raise ValueError('Requires that the `full_name` attribute be set')
        resp = self.http.get('/repos/{r}/branches'.format(r=self.full_name), params={'per_page': 999})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        out = resp.json()

        return [GithubBranch.deserialize(client=self.http, repository=self, obj=branch) for branch in out]

    # ========
    # Metadata
    # ========

    def can(self, perm) -> bool:
        """
        Permissions check for 'admin', 'push', or 'pull' for this repository
        with the logged-in user
        """
        return bool(self.permissions.get(perm, False))

    @property
    def can_admin(self) -> bool:
        return self.can('admin')

    @property
    def can_push(self) -> bool:
        return self.can('push')

    @property
    def can_pull(self) -> bool:
        return self.can('pull')

    @property
    def is_fork(self) -> bool:
        return self.fork

    @property
    def is_private(self) -> bool:
        return self.private

    @property
    def is_public(self) -> bool:
        return not self.private


class GithubBranch(BaseGithubSerializer):
    ALLOWED_MAPS: List[str] = []

    repository: Optional['GithubRepository'] = None
    protection: Optional['GithubBranchProtection'] = None

    def __init__(self, client, name, repository: Optional[GithubRepository] = None, repository_name: Optional[str] = None, **kwargs):
        self.repository = repository or GithubRepository(client, repository_name)

        if 'name' in kwargs:
            del kwargs['name']

        super(GithubBranch, self).__init__(client, name, **kwargs)

    def refresh(self):
        if not isinstance(self.repository, GithubRepository):
            raise ValueError('Requires that the `repository` attribute be set')
        if not self.repository.full_name:
            self.repository.reload()

        resp = self.http.get('/repos/{r}/branches/{b}'.format(r=self.repository.full_name, b=self.name), params={'per_page': 999})
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)

    def _set_props(self, **kwargs):
        if 'protection' in kwargs:
            self.protection = GithubBranchProtection(http=self.http, branch=self, **kwargs['protection'])
        elif not self.protection:
            self.protection = GithubBranchProtection(http=self.http, branch=self)

        super(GithubBranch, self)._set_props(**kwargs)

    @classmethod
    def fetch(cls, client, name, repository=None, repository_name=None) -> 'GithubBranch':
        if not repository:
            repository = GithubRepository.fetch(client, repository_name)

        out = cls(client, name, repository=repository)
        out.refresh()
        return out

    @classmethod
    def deserialize(cls, client: GithubHttp, repository: GithubRepository, obj: Dict[str, Any]) -> 'GithubBranch':
        name = obj.get('name')
        if 'name' in obj:
            del obj['name']

        return cls(client=client, name=name, repository=repository, **obj)

    def __hash__(self):
        if not self.repository.full_name:
            self.repository.reload()

        return hash((self.repository.full_name, self.name))


class GithubBranchProtection(BaseGithubSerializer):
    branch: GithubBranch

    enabled: bool
    required_status_checks: bool
    required_code_review: bool
    up_to_date: bool
    dismiss_stale_reviews: bool
    except_admins: bool
    push_restrictions: bool

    def __init__(self, client: GithubHttp, branch: GithubBranch, **kwargs):
        self.http = client
        self.branch = branch
        self.contexts: List[str] = []
        self.dismissal_users: List[str] = []
        self.dismissal_teams: List[str] = []
        self.push_users: List[str] = []
        self.push_teams: List[str] = []
        self._set_props(**kwargs)

        # This is due to the preview API not containing all the info we need, so we need to
        # hit multiple endpoints and stitch them together
        debug('GRABBING MORE')
        self.__more()

    def _set_props(self, **kwargs):
        # APIs for branch protection are still in preview-mode only as of GHE v2.10, so we'll have
        # to do a lot of manual mapping and changing of names to remain consistent between the 3
        # ways to view it: `/branches`, `/branches/{name}`, and `/branches/{name}/protection`

        super()._set_props(**kwargs)

        # Yes, this is ugly. I'm sorry.
        if 'enabled' in kwargs:
            debug('`enabled` => {}'.format(repr(kwargs['enabled'])))
            self.enabled = kwargs['enabled']
        else:
            debug('`enabled` not found!')

        if 'required_status_checks' in kwargs:
            required_status_checks = kwargs['required_status_checks'] or {}

            if kwargs['required_status_checks'] is None:
                debug('`required_status_checks` => IS NULL')
                self.required_status_checks = False
            elif 'enforcement_level' in required_status_checks:
                debug('`required_status_checks.enforcement_level` => {}'.format(repr(required_status_checks['enforcement_level'])))
                self.enforce_admin = required_status_checks['enforcement_level'] == 'everyone'
                self.required_status_checks = required_status_checks['enforcement_level'] != 'off'
            else:
                debug('`required_status_checks.enforcement_level` not found!')
                self.required_status_checks = True

            if 'strict' in required_status_checks:
                debug('`required_status_checks.strict` => {}'.format(repr(required_status_checks['strict'])))
                self.up_to_date = required_status_checks['strict']
                if self.up_to_date:
                    self.required_status_checks = True
            else:
                debug('`required_status_checks.strict` not found!')

            if 'contexts' in required_status_checks:
                debug('`required_status_checks.contexts` => {}'.format(repr(required_status_checks['contexts'])))
                self.contexts = required_status_checks['contexts']
            else:
                debug('`required_status_checks.contexts` not found!')
        else:
            debug('`required_status_checks` not found!')

        if 'restrictions' in kwargs:
            restrictions = kwargs['restrictions'] or {}

            self.push_restrictions = kwargs['restrictions'] is not None

            if 'users' in restrictions:
                debug('`restrictions.users` => {}'.format(repr(restrictions['users'])))
                self.push_users = restrictions['users']
            else:
                debug('`restrictions.users` not found!')
            if 'teams' in restrictions:
                debug('`restrictions.teams` => {}'.format(repr(restrictions['teams'])))
                self.push_teams = restrictions['teams']
            else:
                debug('`restrictions.teams` not found!')
        else:
            debug('`restrictions` not found!')

        if 'required_pull_request_reviews' in kwargs:
            required_pr_reviews = kwargs['required_pull_request_reviews'] or {}

            self.required_code_review = kwargs['required_pull_request_reviews'] is not None

            if 'dismiss_stale_reviews' in required_pr_reviews:
                debug('`required_pull_request_reviews.dismiss_stale_reviews` => {}'.format(repr(required_pr_reviews['dismiss_stale_reviews'])))
                self.dismiss_stale_reviews = required_pr_reviews['dismiss_stale_reviews']
            else:
                debug('`required_pull_request_reviews.dismiss_stale_reviews` not found!')

            if 'dismissal_restrictions' in required_pr_reviews:
                dismiss_restrict = required_pr_reviews['dismissal_restrictions'] or {}

                if 'users' in dismiss_restrict:
                    debug('`required_pull_request_reviews.dismissal_restrictions.users` => {}'.format(repr(dismiss_restrict['users'])))
                    self.dismissal_users = dismiss_restrict['users']
                else:
                    debug('`required_pull_request_reviews.dismissal_restrictions.users` not found!')
                if 'teams' in dismiss_restrict:
                    debug('`required_pull_request_reviews.dismissal_restrictions.teams` => {}'.format(repr(dismiss_restrict['teams'])))
                    self.dismissal_teams = dismiss_restrict['teams']
                else:
                    debug('`required_pull_request_reviews.dismissal_restrictions.teams` not found!')
            else:
                debug('`required_pull_request_reviews.dismissal_restrictions` not found!')
        else:
            debug('`required_pull_request_reviews` not found!')

        if 'enforce_admins' in kwargs:
            enforce_admins = kwargs['enforce_admins'] or {}

            if 'enabled' in enforce_admins:
                debug('`enforce_admins.enabled` => {}'.format(repr(enforce_admins['enabled'])))
                self.except_admins = not enforce_admins['enabled']
            else:
                debug('`enforce_admins.enabled` not found!')
        else:
            debug('`enforce_admins` not found!')

        if self.enabled is None:  # Last resort
            debug('LAST RESORT REACHED. Assuming branch protection is disabled')
            self.enabled = False

    def refresh(self):
        if not isinstance(self.branch, GithubBranch):
            raise ValueError('Requires that the `branch` attribute be set')
        if not isinstance(self.branch.repository, GithubRepository):
            raise ValueError('Requires that the `repository` attribute be set on the instance of GithubBranch')
        if not self.branch.repository.full_name:
            self.branch.repository.reload()

        url = '/repos/{r}/branches/{b}'.format(r=self.branch.repository.full_name,
                                               b=self.branch.name)
        resp = self.http.get(url, params={'per_page': 999})
        if resp.status_code == 404:
            return
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)
        self.__more()

    @classmethod
    def fetch(cls, client: GithubHttp, branch: GithubBranch) -> 'GithubBranchProtection':
        """
        Easy, user-facing way to retrieve a record from the REST API
        """
        out = cls(client, branch)
        out.refresh()
        return out

    def __more(self):
        if not isinstance(self.branch, GithubBranch):
            raise Exception('Requires that the `branch` attribute be set')
        if not isinstance(self.branch.repository, GithubRepository):
            raise Exception('Requires that the `repository` attribute be set on the instance of GithubBranch')
        if not self.branch.repository.full_name:
            self.branch.repository.reload()

        url = '/repos/{r}/branches/{b}/protection'.format(r=self.branch.repository.full_name,
                                                          b=self.branch.name)
        resp = self.http.get(url, params={'per_page': 999})
        if resp.status_code == 404:
            return
        resp.raise_for_status()
        out = resp.json()
        self._set_props(**out)

    def __hash__(self):
        if not self.branch.repository.full_name:
            self.branch.repository.reload()

        return hash((self.branch.repository.full_name, self.branch.name, 'protection'))
