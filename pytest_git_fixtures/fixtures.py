#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""The actual fixtures, you found them ;)."""

import logging
import shutil
import subprocess

from pathlib import Path
from string import Template
from time import time
from typing import Generator, NamedTuple

import pytest

from _pytest.tmpdir import TempPathFactory

from pytest_gnupg_fixtures import GnuPGKeypair

from .utils import get_embedded_file, get_user_defined_file

LOGGER = logging.getLogger(__name__)


class GITRepo(NamedTuple):
    # pylint: disable=missing-class-docstring
    clone_git_dir: Path
    clone_work_tree: Path
    commit_message: str
    fork: Path
    gitconfig: Path
    gnupg_keypair: GnuPGKeypair
    homedir: Path
    initial_branch: str
    remote_fork: str
    remote_upstream: str
    test_filename: str
    upstream: Path
    work_tree: Path
    work_tree_branch: str
    work_tree_git_dir: Path


@pytest.fixture
def gitconfig(
    pytestconfig: "_pytest.config.Config", tmp_path_factory: TempPathFactory
) -> Generator[Path, None, None]:
    """Provides the location of the templated GIT configuration."""
    name = "gitconfig"
    yield from get_user_defined_file(pytestconfig, name)
    yield from get_embedded_file(tmp_path_factory, name=name)


@pytest.fixture
def git_commit_message() -> str:
    """Provides the commit message of the initial commit to the repository."""
    return f"Initial commit: {time()}."


@pytest.fixture
def git_init_script(
    pytestconfig: "_pytest.config.Config", tmp_path_factory: TempPathFactory
) -> Generator[Path, None, None]:
    """Provides the location of the GIT initialization script."""
    name = "git-init.sh"
    yield from get_user_defined_file(pytestconfig, name)
    yield from get_embedded_file(tmp_path_factory, name=name)


@pytest.fixture
def git_initial_branch_name() -> str:
    """
    Provides the name of the initial branch to use.

    Note: This is only currently used to proved the old "master" branch name for forward compatibility.
          All the plumbing is in place to use this, but as of now it cannot be assumed that git >= 2.28.0
          is commonplace.
    """
    # return f"main-{time()}"
    return "master"


@pytest.fixture
def git_remote_name_fork() -> str:
    """Provides the name of the remote used to reference the fork repository."""
    return f"fork-{time()}"


@pytest.fixture
def git_remote_name_upstream() -> str:
    """Provides the name of the remote used to reference the upstream repository."""
    return f"upstream-{time()}"


@pytest.fixture
def git_repo(
    gitconfig: Path,
    git_commit_message: str,
    git_init_script: Path,
    git_initial_branch_name: str,
    git_remote_name_fork: str,
    git_remote_name_upstream: str,
    git_test_filename: str,
    git_work_tree_branch_name: str,
    gnupg_keypair: GnuPGKeypair,
    tmp_path: Path,
) -> GITRepo:
    """
    Provides a temporary, initialized, GIT repository with a bare upstream, fork, and separate work tree.

    The embedded GIT initialization script performs the following actions:
        1. "upstream" and "fork" created as bare repositories.
        2. "clone" created by cloning upstream.
        3. clone is modified.
        4. clone is pushed to upstream (not the fork).
        5. "work tree" is created from upstream.
    """

    environment = {
        "GNUPGHOME": gnupg_keypair.gnupg_home,
        "HOME": str(tmp_path),
    }

    LOGGER.debug("Initializing GIT Repository ...")

    # Create a GIT configuration from the template ...
    # Note: Must be ".gitconfig", instead of __name__, or git will not find it!
    path_gitconfig = tmp_path.joinpath(".gitconfig")
    (name, email) = gnupg_keypair.uids[0].split("<")
    name = name.strip()
    email = email[:-1]

    template = Template(gitconfig.read_text("utf-8"))
    path_gitconfig.write_text(
        template.substitute(
            {
                "GIT_USER_EMAIL": email,
                "GIT_USER_NAME": name,
                "GIT_USER_SIGNINGKEY": gnupg_keypair.fingerprints[1],
            }
        ),
        "utf-8",
    )

    # Instantiate and execute the GIT initialization script ...
    path_clone = tmp_path.joinpath("clone")
    path_fork = tmp_path.joinpath("fork")
    path_upstream = tmp_path.joinpath("upstream")
    path_work_tree = tmp_path.joinpath("work-tree")
    path_work_tree_git_dir = path_upstream.joinpath("worktrees").joinpath(
        path_work_tree.name
    )
    subprocess.run(
        ["/bin/sh", str(git_init_script)],
        check=True,
        cwd=str(tmp_path),
        env={
            **environment,
            **{
                "GIT_COMMIT_MESSAGE": git_commit_message,
                "GIT_INITIAL_BRANCH_NAME": git_initial_branch_name,
                "GIT_PATH_CLONE": path_clone,
                "GIT_PATH_FORK": path_fork,
                "GIT_PATH_UPSTREAM": path_upstream,
                "GIT_PATH_WORK_TREE": path_work_tree,
                "GIT_REMOTE_NAME_FORK": git_remote_name_fork,
                "GIT_REMOTE_NAME_UPSTREAM": git_remote_name_upstream,
                "GIT_TEST_FILENAME": git_test_filename,
                "GIT_WORK_TREE_BRANCH_NAME": git_work_tree_branch_name,
                "GNUPG_PASSPHRASE": gnupg_keypair.passphrase,
            },
        },
    )

    LOGGER.debug("  clone             : %s", path_clone)
    LOGGER.debug("  commit message    : %s", git_commit_message)
    LOGGER.debug("  fork (bare)       : %s", path_fork)
    LOGGER.debug("  home              : %s", tmp_path)
    LOGGER.debug("  initial branch    : %s", git_initial_branch_name)
    LOGGER.debug("  gitconfig         : %s", path_gitconfig)
    LOGGER.debug("  remote (fork)     : %s", git_remote_name_fork)
    LOGGER.debug("  remote (upstream) : %s", git_remote_name_upstream)
    LOGGER.debug("  test filename     : %s", git_test_filename)
    LOGGER.debug("  upstream (bare)   : %s", path_upstream)
    LOGGER.debug("  work tree         : %s", path_work_tree)
    LOGGER.debug("  work tree branch  : %s", git_work_tree_branch_name)

    yield GITRepo(
        clone_git_dir=path_clone.joinpath(".git"),
        clone_work_tree=path_clone,
        commit_message=git_commit_message,
        fork=path_fork,
        gitconfig=path_gitconfig,
        gnupg_keypair=gnupg_keypair,
        homedir=tmp_path,
        initial_branch=git_initial_branch_name,
        remote_fork=git_remote_name_fork,
        remote_upstream=git_remote_name_upstream,
        test_filename=git_test_filename,
        upstream=path_upstream,
        work_tree=path_work_tree,
        work_tree_branch=git_work_tree_branch_name,
        work_tree_git_dir=path_work_tree_git_dir,
    )
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def git_test_filename() -> str:
    """Provides the name of the test file committed into the repository."""
    return f"test-{time()}.txt"


@pytest.fixture
def git_work_tree_branch_name() -> str:
    """Provides the name of the branch used to create the git work tree."""
    return f"branch-{time()}"
