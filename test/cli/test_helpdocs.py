import sh


def test_gh_refresh():
    sh.gh_refresh('--version')
    sh.gh_refresh('--help')


def test_gh_permit():
    sh.gh_permit('--version')
    sh.gh_permit('--help')


def test_gh_protect():
    sh.gh_protect('--version')
    sh.gh_protect('--help')


def test_gh_releases():
    sh.gh_releases('--version')
    sh.gh_releases('--help')
