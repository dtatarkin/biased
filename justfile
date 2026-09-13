import? '.just'

source_file := source_file()

# This file is a bootstrap entrypoint: the shared modules it forwards to are
# declared in the gitignored `.just`, so in a checkout without one they do not
# resolve — and a *dependency* on a recipe from an unresolved module is a parse
# error, which takes the whole file down rather than the one recipe. So `list`
# inlines `just --list` and every forward into a shared module is a shell-body
# `just <module>::<recipe>` line. Both are the bootstrap-entrypoint exception in
# the shared justfile conventions.

[default]
[doc("List all available recipes")]
list:
    @just --justfile {{ source_file }} --list

[doc("Bootstrap a fresh clone (submodules, uv environment, pre-commit hooks)")]
init:
    #!/usr/bin/env bash
    set -euo pipefail
    just git-submodule::update
    just --justfile {{ source_file }} sync
    just pre-commit::install

[doc("Synchronise the uv-managed virtual environment with pyproject.toml + uv.lock")]
sync:
    uv sync

[doc("Run a command inside the uv-managed virtual environment")]
[positional-arguments]
run *args:
    uv run "$@"

[doc("Create the uv virtual environment if absent and print the activation command")]
shell:
    uv venv --allow-existing 2>&1 | tail -n 1 | sed "s/Activate with: //"

[doc("Bump the dev release segment of the project version")]
[group("release")]
bump-dev:
    uv version --bump dev

[doc("Build the sdist and wheel into dist/")]
[group("release")]
build:
    uv build

[doc("Publish the built distributions to PyPI (credentials from pypi.env)")]
[group("release")]
publish:
    uv run dotenv --file pypi.env run uv publish dist/biased-*

[doc("Run the test suite with pytest (-c pins rootdir here so pytest does not ascend into an enclosing uv workspace)")]
[group("qa")]
[positional-arguments]
test *args="tests":
    just --justfile {{ source_file }} run pytest -c pyproject.toml "$@"

[doc("Run the bandit security linter over src and tests")]
[group("qa")]
[positional-arguments]
bandit *args:
    just --justfile {{ source_file }} run bandit --configfile pyproject.toml "$@" --recursive src tests

[doc("Run the mypy type checker")]
[group("qa")]
[positional-arguments]
mypy *args:
    just --justfile {{ source_file }} run mypy "$@"

[doc("Run the pyright type checker")]
[group("qa")]
[positional-arguments]
pyright *args:
    just --justfile {{ source_file }} run pyright "$@"

[doc("Type-check the project (mypy)")]
[group("qa")]
typecheck: mypy

[doc("Run all linters: pre-commit hooks plus type checking")]
[group("qa")]
lint:
    #!/usr/bin/env bash
    set -euo pipefail
    just pre-commit::run
    just --justfile {{ source_file }} typecheck
