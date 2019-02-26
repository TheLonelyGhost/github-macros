# Changelog

We follow [Semantic Versioning](http://semver.org/) as a way of measuring stability of an update. This
means we will never make a backwards-incompatible change within a major version of the project.

## v2.0.0 (2019-02-26)

- Public release of previously closed-source application (renamed to `github_macros` to work with PyPi)

## v1.1.0 (2019-02-24)

- Adds `gh-releases` command for quickly getting download URLs for each uploaded asset of a given release.

## v1.0.1 (2019-02-24)

- FIX: public GitHub has a different base url entirely `https://api.github.com` vs `https://{domain}/api/v3` for GitHub Enterprise

## v1.0.0 (2019-01-08)

- Removes references to ExactTarget
- Defaults to using public GitHub, with references to the `GITHUB_DOMAIN` as an override

## v0.8.1 (2018-12-10)

- Fixes alignment of `REPO:` part of output when cloning a repo instead of updating it in-place

## v0.8.0 (2018-11-16)

- Notifies if additional directories are found which aren't repositories for `gh-refresh`

## v0.7.2 (2018-09-27)

- Fixes "AttributeError: 'function' object has no attribute 'clone'" for `gh-refresh`

## v0.7.1 (2018-09-12)

- Fixes problem when cloning/updating too many repositories in a row (exit code 128, "ssh_exchange_identification: read: Connection reset by peer")

## v0.7.0 (2018-08-27)

- Adds `--ci-check` flag (one or more times) to `gh-protect` command for checking if a specific CI commit status is set as required for a PR

## v0.6.0 (2018-08-22)

- Adds `gh-permit` command for handling assignment of permissions for all repos in an organization on a per-team basis

## v0.5.1 (2018-05-30)

- Fixes bug with `--clobber` handling a remote repo that (once) contained no commits in the log and was synced

## v0.5.0 (2018-05-29)

- Adds `--clobber` option for `gh-refresh`, in order to force the local `master` branch to be in-line with `origin`'s copy of `master`

## v0.4.0 (2018-03-26)

- Bugfixes with instantiating GitHub Repository model
- Allows GitHub models to be compared for same-ness, for use with `set()`
- Adheres to proper GitHub API versioning headers (`Accept: application/vnd.github.loki-preview+json`)
- Adds models for repository branches and their protections
- Restructures documentation with restructuredtext format in multiple files
- Adds GIF demonstrations of command output

## v0.3.0 (2018-03-22)

- Adds model for GitHub User
- Adds model for GitHub Repository
- Adds model for GitHub Organization
- Adds `GithubHttp` for easier creation and more consistent use of HTTP client (might work with public GitHub too?)
- Allows for serialization and deserialization to/from (partial) JSON to a given model
- Models allow for refreshing content from API data

## v0.2.0 (2018-02-20)

- BREAKING: Changed flag `--users` to `--user` to be more consistent with singular `--organization` multi-use flags

## v0.1.0 (2018-02-20)

- Initial version release
