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

ERRORS=

for release in noble bookworm trixie forky sid; do
  echo
  echo Publishing ${release}
  for i in `find ${DEB_BASEDIR}/${release}-${DEB_ARCH} -name \*.deb`; do
    echo Publishing deb ${i};
    # ignore errors for now to not fail when packages are built multiple times with the same version
    reprepro -b ${REPO_BASEDIR}/debian/${release} --component main includedeb ${release} ${i} || ERRORS="${ERRORS} `basename $i`"
  done

  echo
  echo Checking ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} check

  echo
  echo Checking Pool ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} checkpool
done

COUNTS=
for release in noble bookworm trixie forky sid; do
  echo
  echo Listing ${release}
  reprepro -b ${REPO_BASEDIR}/debian/${release} list ${release}
  COUNTS="${COUNTS} ${release}: `reprepro -b ${REPO_BASEDIR}/debian/${release} list ${release} | wc -l`"
done

# print out errors, but sort the list of failed deb-files and remove duplicates
echo
echo Errors:
for error in `echo ${ERRORS} | xargs -n1 | sort -u | xargs`;do
  echo "- ${error}"
done
echo
echo Done, package counts: ${COUNTS}
