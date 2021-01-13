# pytest-git-fixtures

## Overview

Pytest fixtures to dynamically create [GIT](https://git-scm.com/) repositories for testing.

## Getting Started

Update <tt>setup.py</tt> to include:

```python
setup(
	tests_require=["pytest-git-fixtures"]
)
```

All fixtures should be automatically included via the <tt>pytest11</tt> entry point.

```python
import logging
import subprocess
import pytest
from pytest_git_fixtures import GITRepo  # Optional, for typing

LOGGER = logging.getLogger(__name__)

def test_sanity_check(git_repo: GITRepo):
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
```

* Tested with python 3.8

## Installation
### From [pypi.org](https://pypi.org/project/pytest-git-fixtures/)

```
$ pip install pytest_git_fixtures
```

### From source code

```bash
$ git clone https://github.com/crashvb/pytest-git-fixtures
$ cd pytest-git-fixtures
$ virtualenv env
$ source env/bin/activate
$ python -m pip install --editable .[dev]
```

## Fixtures

### <a name="gitconfig"></a> gitconfig

Provides the path to a templated GIT configuration file that is used to initialize the repository. If a user-defined script (<tt>tests/gitconfig</tt>) can be located, it is used. Otherwise, an embedded configuration template is copied to temporary location and returned. This fixture is used by the [git_repo](#git_repo) fixture.

The`$GIT_USER_EMAIL`, `$GIT_USER_NAME`, and `$GIT_SIGNINGKEY` variables will be populated within the template during generation of the repository.

### <a name="gitrepo"></a> gitrepo

Initializes a temporary GIT repository with a bare upstream, fork, and separate work tree.

#### NamedTuple Fields

The following fields are defined in the tuple provided by this fixture:

* **fork** - Path to the "fork" git-dir.
* **homedir** - Path to the home directory used to initialize the repo.
* **gitconfig** - Path to the fully instantiated git configuration, created from [gitconfig](#gitconfig)
* **gnupg** - The GnuPG keypair used to sign commits, from [gnupg_keypair](pytest_gnupg_fixtures#gnupg_keypair)
* **clone_git_dir** - Path to the "clone" git-dir.
* **clone_work_tree** - Path to the "clone" work tree.
* **upstream** - Path to the "upstream" git-dir.
* **work_tree** - Path to the separate "work tree" work tree.

Typing is provided by `pytest_git_fixtures.GITRepo`.

### <a name="git_init_script"></a> git_init_script

Provides the path to a GIT initialization script that is used to create repository structure. If a user-defined script (<tt>tests/git-init.sh</tt>) can be located, it is used. Otherwise, an embedded script is copied to temporary location and returned. This fixture is used by the [git_repo](#git_repo) fixture.

The`$GIT_PATH_CLONE`, `$GIT_PATH_FORK`, `$GIT_PATH_UPSTREAM`, `$GIT_PATH_WORK_TREE`, `GNUPGHOME`, `GNUPG_PASSPHRASE`, and `HOME` environment variables will be populated during invocation of the script.

## <a name="limitations"></a>Limitations

1. This has been coded to work with git-scm >= 2.6.
2. The generated repository is very simple. TBD if this will be expanded to support a more realistic configuration.
4. The embedded GIT configuration is configured to sign commits and tags by default. This can cause complications with externally configured instances of GnuPG, unless they are configured to use loopback for pinentry, or you like testing with interactive passphrase entry ;) . It is recommended that [pytest-gnupg-fixtures](https://pypi.org/project/pytest-gnupg-fixtures/) be used. This packages provides a `gpg-wrapper` script that can be used in conjuction with the git `gpg.program` configuration value as follows:

```python
def test_something_with_gnupg(git_repo: GITRepo):
    subprocess.run(
        [
            "git",
            "-c",
            f"gpg.program={git_repo.gnupg_keypair.gnupg_home}/gpg-wrapper",
            "commit",
            "--message",
            "Look Ma, no hands!",
        ],
        check=True,
        cwd=str(git_repo.clone_work_tree),
        env={**environment, **{"GNUPG_PASSPHRASE": git_repo.gnupg_keypair.passphrase}},
    )
```

## Changelog

### 0.1.0 (2021-01-11)

* Initial release.

## Development

[Source Control](https://github.com/crashvb/pytest-git-fixtures)
