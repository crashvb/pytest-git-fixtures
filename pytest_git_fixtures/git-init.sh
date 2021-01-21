#!/bin/sh

set -e

# TODO: Add --initial-branch="${GIT_INITIAL_BRANCH_NAME}" to git-init and / or git-clone when git-2.28.0
#       becomes commonplace.

# Initialize an bare repositories ...
git init --bare "${GIT_PATH_FORK}"
git init --bare "${GIT_PATH_UPSTREAM}"

# Clone the bare repository to populate the initial branch
# (or it will not be possible to create a work tree) ...
git clone \
	--dissociate \
	--no-hardlinks \
	--no-local \
	--origin="${GIT_REMOTE_NAME_UPSTREAM}" \
	"${GIT_PATH_UPSTREAM}" \
	"${GIT_PATH_CLONE}"

# Add the remote to the fork ...
cd "${GIT_PATH_CLONE}" && git remote add "${GIT_REMOTE_NAME_FORK}" "${GIT_PATH_FORK}"

# Modify the clone to be in a "useful" state ...
cat <<- EOF > "${GIT_PATH_CLONE}/${GIT_TEST_FILENAME}"
	This is a test file created on $(date +%Y-%m-%d_%H:%M:%S).
EOF
cd "${GIT_PATH_CLONE}" && \
	git add "${GIT_TEST_FILENAME}" && \
	git -c "gpg.program=${GNUPGHOME}/gpg-wrapper" commit --message="${GIT_COMMIT_MESSAGE}" && \
	git push "${GIT_REMOTE_NAME_UPSTREAM}" "${GIT_INITIAL_BRANCH_NAME}"

# Create a work tree with a new branch ...
git --git-dir="${GIT_PATH_UPSTREAM}" worktree add -b "${GIT_WORK_TREE_BRANCH_NAME}" "${GIT_PATH_WORK_TREE}"

