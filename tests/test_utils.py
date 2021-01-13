#!/usr/bin/env python

# pylint: disable=redefined-outer-name

"""pytest fixture tests."""

import logging

from pytest_git_fixtures import get_user_defined_file

LOGGER = logging.getLogger(__name__)


def test_get_user_defined_file(pytestconfig: "_pytest.config.Config"):
    """Tests that the user defined check fails here."""

    for _ in get_user_defined_file(pytestconfig, "does_not_exist"):
        assert False
