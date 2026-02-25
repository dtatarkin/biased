import "just.just"
import "git.just"
import "django.just"

[group("project")]
shell:
    uv venv --allow-existing 2>&1 | tail -n 1 | sed "s/Activate with: //"

[group("project")]
bump-dev:
    uv version --bump dev

[group("project")]
build:
    uv build

[group("project")]
python-run *args:
    @uv run {{ args }}

[group("project")]
publish:
    just python-run dotenv --file pypi.env run uv publish dist/biased-*

[group("linting")]
pre-commit-autoupdate:
    just python-run pre-commit autoupdate

[group("linting")]
format: format-justfiles
    -just python-run ruff format
    -just python-run ruff check --fix

[group("linting")]
pre-commit: format
    -just python-run pre-commit run --all-files

[group("linting")]
bandit *args:
    -just python-run bandit --configfile pyproject.toml {{ args }} --recursive src tests

[group("linting")]
mypy *args:
    just python-run mypy {{ args }}

[group("linting")]
pyright *args:
    just python-run pyright {{ args }}

[group("linting")]
typecheck: mypy

[group("linting")]
lint: pre-commit typecheck
