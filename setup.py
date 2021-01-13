#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages


def find_version(*segments):
    root = os.path.abspath(os.path.dirname(__file__))
    abspath = os.path.join(root, *segments)
    with open(abspath, "r") as file:
        content = file.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string!")


setup(
    author="Richard Davis",
    author_email="crashvb@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    description="Pytest fixtures for testing with git.",
    entry_points={"pytest11": ["git_fixtures = pytest_git_fixtures"]},
    extras_require={"dev": ["black", "pylint", "twine", "wheel"]},
    include_package_data=True,
    install_requires=["pytest", "pytest_gnupg_fixtures"],
    keywords="fixtures git git-scm pytest",
    license="GNU General Public License v3.0",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    name="pytest_git_fixtures",
    packages=find_packages(),
    package_data={"pytest_git_fixtures": ["gitconfig", "git-init.sh"]},
    test_suite="tests",
    url="https://pypi.org/project/pytest-git-fixtures/",
    version=find_version("pytest_git_fixtures", "__init__.py"),
)
