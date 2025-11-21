#!/bin/bash
#
#
# Add all debian packages to the local repository
#
# This requires to run the Ansible playbook 'debian-repository-github.yml' once

set -eu

REPO_BASEDIR=/opt/cowbuilder/aptrepo
DEB_BASEDIR=/opt/cowbuilder/github
DEB_ARCH=amd64

for release in noble bookworm trixie forky sid; do
  echo
  echo Publishing ${release}
  for i in `find ${DEB_BASEDIR}/${release}-${DEB_ARCH} -name \*.deb`; do
    echo Publishing deb ${i};
    reprepro -b ${REPO_BASEDIR}/debian/${release} --component main includedeb ${release} ${i}
  done

  echo
  echo Checking ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} check

  echo
  echo Checking Pool ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} checkpool
done

for release in noble bookworm trixie forky sid; do
  echo
  echo Listing ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} list ${release}
done

echo Done
