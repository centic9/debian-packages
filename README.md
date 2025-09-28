# debian-packages
A helper repo to host Github Actions to build Debian packages out of Github repositories

# debian-package-debcraft.yml

Use this action if you would like to build Debian packages out of GitHub Actions. GitHub Actions only offer Ubuntu-based runners, but debcraft allows to build packages for different releases of both Debian and Ubuntu.

Unfortunately you cannot put a file in the directory .github/workflows directly in a project which hosts a Debian package as it would fail to build due to changes to the source.

A possible solution is to host the building logic in a separate repository and fetch the proper sources for the package via parameters to the workflow.

See [debian-package-debcraft.yml](https://github.com/centic9/debian-packages/blob/main/.github/workflows/debian-package-debcraft.yml) for a resulting Github Action which can build any package as long as sources are available in a repository on GitHub.
