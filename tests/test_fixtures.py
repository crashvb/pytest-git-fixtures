#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""pytest fixture tests."""

import logging
import subprocess

from pathlib import Path

from pytest_git_fixtures import GITRepo

LOGGER = logging.getLogger(__name__)


def test_gitconfig(gitconfig: Path):
    """Test that a GIT configuration can be generated."""
    assert gitconfig.exists()


def test_git_commit_message(git_commit_message: str):
    """Test that a GIT commit message can be generated."""
    assert git_commit_message
    assert git_commit_message != "Initial commit: ."


def test_git_init_script(git_init_script: Path):
    """Test that a GIT initialization script can be generated."""
    assert git_init_script.exists()


def test_git_initial_branch_name(git_initial_branch_name: str):
    """Test that a GIT branch name can be generated."""
    assert git_initial_branch_name
    # TODO: Update this when the fixture is updated.
    # assert git_initial_branch_name != "main-"
    assert git_initial_branch_name == "master"


def test_git_remote_name_fork(git_remote_name_fork: str):
    """Test that a GIT remote name can be generated."""
    assert git_remote_name_fork
    assert git_remote_name_fork != "fork-"


def test_git_remote_name_upstream(git_remote_name_upstream: str):
    """Test that a GIT remote name can be generated."""
    assert git_remote_name_upstream
    assert git_remote_name_upstream != "upstream-"


def test_git_repo(git_repo: GITRepo):
    """Test that a GIT repository can be initialized."""
    assert git_repo.clone_git_dir.exists()
    assert git_repo.clone_work_tree.exists()
    assert git_repo.commit_message
    assert git_repo.fork.exists()

    assert git_repo.gitconfig.exists()
    gitconfig = git_repo.gitconfig.read_text("utf-8")
    assert "$GIT" not in gitconfig

    assert git_repo.gnupg_keypair
    assert git_repo.homedir.exists()
    assert git_repo.initial_branch
    assert git_repo.remote_fork
    assert git_repo.remote_upstream
    assert git_repo.test_filename
    assert git_repo.upstream.exists()
    assert git_repo.work_tree.exists()
    assert git_repo.work_tree_branch
    assert git_repo.work_tree_git_dir.exists()


def test_git_test_filename(git_test_filename: str):
    """Test that a GIT test filename can be generated."""
    assert git_test_filename
    assert git_test_filename != "test-.txt"


def test_git_work_tree_branch_name(git_work_tree_branch_name: str):
    """Test that a GIT branch name can be generated."""
    assert git_work_tree_branch_name
    assert git_work_tree_branch_name != "branch-"


def test_sanity_check(git_repo: GITRepo):
    """Test that the clone and work tree are valid."""
    environment = {
        "GNUPGHOME": git_repo.gnupg_keypair.gnupg_home,
        "HOME": str(git_repo.homedir),
    }
    completed_process = subprocess.run(
        ["git", "log", "--show-signature"],
        capture_output=True,
        check=True,
        cwd=str(git_repo.clone_work_tree),
        env=environment,
    )
    stdout = completed_process.stdout.decode("utf-8")
    LOGGER.debug(stdout)
    assert "Good signature from" in stdout
    assert git_repo.commit_message in stdout

    completed_process = subprocess.run(
        ["git", "log", "--show-signature"],
        capture_output=True,
        check=True,
        cwd=str(git_repo.work_tree),
        env={**environment, **{"GIT_DIR": str(git_repo.upstream)}},
    )
    stdout = completed_process.stdout.decode("utf-8")
    LOGGER.debug(stdout)
    assert "Good signature from" in stdout
    assert git_repo.commit_message in stdout
