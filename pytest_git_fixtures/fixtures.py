#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""The actual fixtures, you found them ;)."""

import logging
import shutil
import subprocess

from pathlib import Path
from string import Template
from typing import Generator, NamedTuple

import pytest

from _pytest.tmpdir import TempPathFactory

from pytest_gnupg_fixtures import GnuPGKeypair

from .utils import get_embedded_file, get_user_defined_file

LOGGER = logging.getLogger(__name__)


class GITRepo(NamedTuple):
    # pylint: disable=missing-class-docstring
    fork: Path
    homedir: Path
    gitconfig: Path
    gnupg_keypair: GnuPGKeypair
    clone_git_dir: Path
    clone_work_tree: Path
    upstream: Path
    work_tree: Path


@pytest.fixture
def gitconfig(
    pytestconfig: "_pytest.config.Config", tmp_path_factory: TempPathFactory
) -> Generator[Path, None, None]:
    """Provides the location of the templated GIT configuration."""
    name = "gitconfig"
    yield from get_user_defined_file(pytestconfig, name)
    yield from get_embedded_file(tmp_path_factory, name=name)


@pytest.fixture
def git_repo(
    gitconfig: Path, git_init_script: Path, gnupg_keypair: GnuPGKeypair, tmp_path: Path
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
    subprocess.run(
        ["/bin/sh", str(git_init_script)],
        check=True,
        cwd=str(tmp_path),
        env={
            **environment,
            **{
                "GIT_PATH_CLONE": path_clone,
                "GIT_PATH_FORK": path_fork,
                "GIT_PATH_UPSTREAM": path_upstream,
                "GIT_PATH_WORK_TREE": path_work_tree,
                "GNUPG_PASSPHRASE": gnupg_keypair.passphrase,
            },
        },
    )

    LOGGER.debug("  fork      : %s", path_fork)
    LOGGER.debug("  home      : %s", tmp_path)
    LOGGER.debug("  gitconfig : %s", path_gitconfig)
    LOGGER.debug("  clone     : %s", path_clone)
    LOGGER.debug("  upstream  : %s", path_upstream)
    LOGGER.debug("  work tree : %s", path_work_tree)

    yield GITRepo(
        fork=path_fork,
        homedir=tmp_path,
        gitconfig=path_gitconfig,
        gnupg_keypair=gnupg_keypair,
        clone_git_dir=path_clone.joinpath(".git"),
        clone_work_tree=path_clone,
        upstream=path_upstream,
        work_tree=path_work_tree,
    )
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def git_init_script(
    pytestconfig: "_pytest.config.Config", tmp_path_factory: TempPathFactory
) -> Generator[Path, None, None]:
    """Provides the location of the GIT initialization script."""
    name = "git-init.sh"
    yield from get_user_defined_file(pytestconfig, name)
    yield from get_embedded_file(tmp_path_factory, name=name)
