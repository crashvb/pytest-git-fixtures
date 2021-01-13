#!/usr/bin/env python

"""Utility classes."""

import logging

from importlib.resources import read_text
from pathlib import Path
from typing import Generator

from _pytest.tmpdir import TempPathFactory

LOGGER = logging.getLogger(__name__)


def get_embedded_file(
    tmp_path_factory: TempPathFactory, *, delete_after: bool = True, name: str
) -> Generator[Path, None, None]:
    """
    Replicates a file embedded within this package to a temporary file.

    Args:
        tmp_path_factory: Factory to use when generating temporary paths.
        delete_after: If True, the temporary file will be removed after the iteration is complete.
        name: The name of the embedded file to be replicated.

    Yields:
        The path to the temporary file.
    """
    tmp_path = tmp_path_factory.mktemp(__name__).joinpath(name)
    with tmp_path.open("w") as file:
        file.write(read_text(__package__, name))
    yield tmp_path
    if delete_after:
        tmp_path.unlink(missing_ok=True)


def get_user_defined_file(pytestconfig: "_pytest.config.Config", name: str):
    """
    Tests to see if a user-defined file exists.

    Args:
        pytestconfig: pytest configuration file to use when locating the user-defined file.
        name: Name of the user-defined file.

    Yields:
        The path to the user-defined file.
    """
    user_defined = Path(str(pytestconfig.rootdir), "tests", name)
    if user_defined.exists():
        yield user_defined
