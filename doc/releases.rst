========
Releases
========
-----------
gh-releases
-----------

Handles listing uploaded release assets, in a ``grep``-able format for filtering, and spits out the links to download them.

.. TODO:  Insert GIF of asciicast

One might get the following output:

.. code-block:: bash

   $ gh-releases jwilhm/alacritty
   v0.2.3	Alacritty-v0.2.3-x86_64.tar.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.3/Alacritty-v0.2.3-x86_64.tar.gz
   v0.2.3	Alacritty-v0.2.3.dmg	https://github.com/jwilm/alacritty/releases/download/v0.2.3/Alacritty-v0.2.3.dmg
   v0.2.3	Alacritty-v0.2.3.exe	https://github.com/jwilm/alacritty/releases/download/v0.2.3/Alacritty-v0.2.3.exe
   v0.2.3	Alacritty-v0.2.3_amd64.deb	https://github.com/jwilm/alacritty/releases/download/v0.2.3/Alacritty-v0.2.3_amd64.deb
   v0.2.3	alacritty.1.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.3/alacritty.1.gz
   v0.2.3	alacritty.yml	https://github.com/jwilm/alacritty/releases/download/v0.2.3/alacritty.yml
   v0.2.3	alacritty_macos.yml	https://github.com/jwilm/alacritty/releases/download/v0.2.3/alacritty_macos.yml
   v0.2.3	alacritty_windows.yml	https://github.com/jwilm/alacritty/releases/download/v0.2.3/alacritty_windows.yml
   v0.2.3	winpty-agent.exe	https://github.com/jwilm/alacritty/releases/download/v0.2.3/winpty-agent.exe
   v0.2.4	alacritty-completions.bash	https://github.com/jwilm/alacritty/releases/download/v0.2.4/alacritty-completions.bash
   ---8<--- [SNIP] ---8<---
   v0.2.8	alacritty.1.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.8/alacritty.1.gz
   v0.2.8	alacritty.yml	https://github.com/jwilm/alacritty/releases/download/v0.2.8/alacritty.yml
   v0.2.9	Alacritty-v0.2.9-i386.tar.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9-i386.tar.gz
   v0.2.9	Alacritty-v0.2.9-windows.zip	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9-windows.zip
   v0.2.9	Alacritty-v0.2.9-x86_64.tar.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9-x86_64.tar.gz
   v0.2.9	Alacritty-v0.2.9.dmg	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9.dmg
   v0.2.9	Alacritty-v0.2.9_amd64.deb	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9_amd64.deb
   v0.2.9	Alacritty-v0.2.9_i386.deb	https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9_i386.deb
   v0.2.9	alacritty.1.gz	https://github.com/jwilm/alacritty/releases/download/v0.2.9/alacritty.1.gz


Usage
=====

.. code-block:: bash

    $ gh-refresh --help
    usage: gh-releases [-h] [--version] [--github-user GH_USER]
                       [--github-token GH_TOKEN] [--prefix PFX]
                       [--pattern VERSION_PATTERN] [--latest]
                       REPO

    positional arguments:
      REPO                  The target repository for which to find the latest
                            version (e.g., "postmodern/chruby")

    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         Prints the program version and exits
      --github-user GH_USER
      --github-token GH_TOKEN
      --prefix PFX          Version prefix applied to semver tags
      --pattern VERSION_PATTERN
                            A python-based regular expression for what pattern
                            indicates a version tag
      --latest              Grab only the latest release

If you don't want to embed your GitHub user credentials, ``--github-user`` defaults to the environment variable ``GITHUB_USER`` and ``--github-token`` defaults to ``GITHUB_TOKEN``.

Examples
========

.. TODO:  Insert GIF of asciicast

Latest *.deb file
-----------------

.. code-block:: bash

    $ gh-releases --latest jwilm/alacritty | awk '/\.deb/ { print($3) }'
    https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9_amd64.deb
    https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9_i386.deb

All *.dmg files
---------------

.. code-block:: bash

    $ gh-releases jwilm/alacritty | awk '/\.dmg/ { print($3) }'
    https://github.com/jwilm/alacritty/releases/download/v0.2.3/Alacritty-v0.2.3.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.4/Alacritty-v0.2.4.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.5/Alacritty-v0.2.5.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.6/Alacritty-v0.2.6.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.7/Alacritty-v0.2.7.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.8/Alacritty-v0.2.8.dmg
    https://github.com/jwilm/alacritty/releases/download/v0.2.9/Alacritty-v0.2.9.dmg
