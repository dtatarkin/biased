import? '.just'

source_file := source_file()

# List all available recipes
[default]
list: (just::list source_file)

# Bootstrap a fresh clone (submodules, uv environment, pre-commit hooks)
init: git-submodule::update sync pre-commit::install

# Synchronise the uv-managed virtual environment with pyproject.toml + uv.lock
sync:
    uv sync

# Run a command inside the uv-managed virtual environment
run *args:
    uv run {{ args }}

# Create the uv virtual environment if absent and print the activation command
shell:
    uv venv --allow-existing 2>&1 | tail -n 1 | sed "s/Activate with: //"

# Bump the dev release segment of the project version
bump-dev:
    uv version --bump dev

# Build the sdist and wheel into dist/
build:
    uv build

# Publish the built distributions to PyPI (credentials from pypi.env)
publish:
    uv run dotenv --file pypi.env run uv publish dist/biased-*

# Run the bandit security linter over src and tests
bandit *args: (run "bandit" "--configfile" "pyproject.toml" args "--recursive" "src" "tests")

# Run the mypy type checker
mypy *args: (run "mypy" args)

# Run the pyright type checker
pyright *args: (run "pyright" args)

# Type-check the project (mypy)
typecheck: mypy

# Run all linters: pre-commit hooks plus type checking
lint: pre-commit::run typecheck
