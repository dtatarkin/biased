import? '.just'

source_file := source_file()

[default]
[doc("List all available recipes")]
list: (just::list source_file)

[doc("Bootstrap a fresh clone (submodules, uv environment, pre-commit hooks)")]
init: git-submodule::update sync pre-commit::install

[doc("Synchronise the uv-managed virtual environment with pyproject.toml + uv.lock")]
sync:
    uv sync

[doc("Run a command inside the uv-managed virtual environment")]
run *args:
    uv run {{ args }}

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

[doc("Run the test suite with pytest")]
[group("qa")]
test *args: (run "pytest" args)

[doc("Run the bandit security linter over src and tests")]
[group("qa")]
bandit *args: (run "bandit" "--configfile" "pyproject.toml" args "--recursive" "src" "tests")

[doc("Run the mypy type checker")]
[group("qa")]
mypy *args: (run "mypy" args)

[doc("Run the pyright type checker")]
[group("qa")]
pyright *args: (run "pyright" args)

[doc("Type-check the project (mypy)")]
[group("qa")]
typecheck: mypy

[doc("Run all linters: pre-commit hooks plus type checking")]
[group("qa")]
lint: pre-commit::run typecheck
