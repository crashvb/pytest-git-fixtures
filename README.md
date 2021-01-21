# pytest-git-fixtures

## Overview

Pytest fixtures to dynamically create [GIT](https://git-scm.com/) repositories for testing.

## Getting Started

Update <tt>setup.py</tt> to include:

```python
from distutils.core import setup

setup(
	tests_require=["pytest-git-fixtures"]
)
```

All fixtures should be automatically included via the <tt>pytest11</tt> entry point.

```python
import logging
import subprocess
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

The`GIT_USER_EMAIL`, `GIT_USER_NAME`, and `GIT_SIGNINGKEY` variables will be populated within the template during generation of the repository.

### <a name="git_commit_message"></a> git_commit_message

Provides the commit message of the initial commit to the repository. This fixture is used by the [git_repo](#git_repo) fixture.

### <a name="git_init_script"></a> git_init_script

Provides the path to a GIT initialization script that is used to create repository structure. If a user-defined script (<tt>tests/git-init.sh</tt>) can be located, it is used. Otherwise, an embedded script is copied to temporary location and returned. This fixture is used by the [git_repo](#git_repo) fixture.

The `GIT_COMMIT_MESSAGE`, `GIT_INITIAL_BRANCH_NAME`, `GIT_PATH_CLONE`, `GIT_PATH_FORK`, `GIT_PATH_UPSTREAM`, `GIT_PATH_WORK_TREE`, `GIT_REMOTE_NAME_FORK`, `GIT_REMOTE_NAME_UPSTREAM`, `GIT_TEST_FILENAME`, `GIT_WORK_TREE_BRANCH_NAME`, `GNUPGHOME`, `GNUPG_PASSPHRASE`, and `HOME` environment variables will be populated during invocation of the script.

### <a name="git_initial_branch_name"></a> git_initial_branch_name.

Provides the name of the initial branch to use. This fixture is used by the [git_repo](#git_repo) fixture.

### <a name="git_remote_name_fork"></a> git_remote_name_fork

Provides the name of the remote used to reference the fork repository. This fixture is used by the [git_repo](#git_repo) fixture.

### <a name="git_remote_name_upstream"></a> git_remote_name_upstream

Provides the name of the remote used to reference the upstream repository. This fixture is used by the [git_repo](#git_repo) fixture.

### <a name="git_repo"></a> git_repo

Initializes a temporary GIT repository with a bare upstream, fork, and separate work tree.

#### NamedTuple Fields

The following fields are defined in the tuple provided by this fixture:

* **clone_git_dir** - Path to the "clone" git-dir.
* **clone_work_tree** - Path to the "clone" work tree.
* **commit_message** - Commit message of the initial commit, created from [git_commit_message](#git_commit_message)
* **fork** - Path to the "fork" git-dir.
* **gitconfig** - Path to the fully instantiated git configuration, created from [gitconfig](#gitconfig)
* **gnupg** - The GnuPG keypair used to sign commits, from [gnupg_keypair](pytest_gnupg_fixtures#gnupg_keypair)
* **homedir** - Path to the home directory used to initialize the repo.
* **initial_branch** - Name of the initial branch, created from [git_initial_branch_name](#git_initial_branch_name)
* **remote_fork** - Name of the remote for the "fork", created from [git_remote_name_fork](#git_remote_name_fork)
* **remote_upstream** - Name of the remote for the "upstream", created from [git_remote_name_upstream](#git_remote_name_upstream)
* **test_filename** - Name of the test file, created from [git_test_filename](#git_test_filename)
* **upstream** - Path to the "upstream" git-dir.
* **work_tree** - Path to the separate "work tree" work tree.
* **work_tree_branch** - Name of the "work tree" branch, created from [git_work_tree_branch_name](#git_work_tree_branch_name)
* **work_tree_git_dir** - Path to the "work tree" git-dir.

Typing is provided by `pytest_git_fixtures.GITRepo`.

### <a name="git_test_filename"></a> git_test_filename

Provides the name of the test file committed into the repository. This fixture is used by the [git_repo](#git_repo) fixture.

### <a name="git_work_tree_branch_name"></a> git_work_tree_branch_name

Provides the name of the branch used to create the git work tree. This fixture is used by the [git_repo](#git_repo) fixture.

## <a name="limitations"></a>Limitations

1. This has been coded to work with git-scm >= 2.6.
2. The generated repository is very simple. TBD if this will be expanded to support a more realistic configuration.
4. The embedded GIT configuration is configured to sign commits and tags by default. This can cause complications with externally configured instances of GnuPG, unless they are configured to use loopback for pinentry, or you like testing with interactive passphrase entry ;) . It is recommended that [pytest-gnupg-fixtures](https://pypi.org/project/pytest-gnupg-fixtures/) be used. This package provides a `gpg-wrapper` script that can be used in conjunction with the git `gpg.program` configuration value as follows:

```python
import subprocess
from pytest_git_fixtures import GITRepo  # Optional, for typing
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
        env={"GNUPG_PASSPHRASE": git_repo.gnupg_keypair.passphrase},
    )
```

## Changelog

### 0.1.0 (2021-01-11)

* Initial release.

## Development

[Source Control](https://github.com/crashvb/pytest-git-fixtures)
