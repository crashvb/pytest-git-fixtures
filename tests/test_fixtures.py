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


def test_git_repo(git_repo: GITRepo):
    """Test that a GIT repository can be initialized."""
    assert git_repo.homedir.exists()


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
    assert "Initial commit." in stdout

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
    assert "Initial commit." in stdout
