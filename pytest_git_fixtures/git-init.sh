#!/bin/sh

set -e

# Initialize an bare repositories ...
git init --bare "${GIT_PATH_FORK}"
git init --bare "${GIT_PATH_UPSTREAM}"

# Clone the bare repository to populate the master branch
# (or it will not be possible to create a work tree) ...
git clone "${GIT_PATH_UPSTREAM}" "${GIT_PATH_CLONE}"

# Add the remote to the fork ...
cd "${GIT_PATH_CLONE}" && git remote add fork "${GIT_PATH_FORK}"

# Modify the clone to be in a "useful" state ...
path_file=test.txt
cat <<- EOF > "${GIT_PATH_CLONE}/${path_file}"
	This is a test file created on $(date +%Y-%m-%d_%H:%M:%S).
EOF
cd "${GIT_PATH_CLONE}" && \
	git add "$path_file" && \
	git -c "gpg.program=${GNUPGHOME}/gpg-wrapper" commit --message="Initial commit." && \
	git push origin master

# Create a work tree for the master branch ...
git --git-dir="${GIT_PATH_UPSTREAM}" worktree add --force "${GIT_PATH_WORK_TREE}" master

