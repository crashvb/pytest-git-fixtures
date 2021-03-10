#!/bin/sh

# set -e

cat <<- EOF
	-------------------------------------
 	 Verification of pytest-git-fixtures
	-------------------------------------
EOF
echo "Upstream:"
set -x
git --git-dir="${GIT_PATH_UPSTREAM}" branch --verbose
git --git-dir="${GIT_PATH_UPSTREAM}" log --all --decorate --graph --oneline --show-signature
set +x

echo "Fork:"
set -x
git --git-dir="${GIT_PATH_FORK}" branch --verbose
git --git-dir="${GIT_PATH_FORK}" log --all --decorate --graph --oneline --show-signature
set +x

echo "Clone:"
set -x
git --git-dir="${GIT_PATH_CLONE}/.git" branch --verbose
git --git-dir="${GIT_PATH_CLONE}/.git" log --all --decorate --graph --oneline --show-signature
git --git-dir="${GIT_PATH_CLONE}/.git" remote --verbose
ls -l "${GIT_PATH_CLONE}"
set +x

echo "Work Tree:"
set -x
git --git-dir="${GIT_PATH_WORK_TREE}/.git" branch --verbose
git --git-dir="${GIT_PATH_WORK_TREE}/.git" log --all --decorate --graph --oneline --show-signature
git --git-dir="${GIT_PATH_WORK_TREE}/.git" remote --verbose
ls -l "${GIT_PATH_WORK_TREE}"
set +x
