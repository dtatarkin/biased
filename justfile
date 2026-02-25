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
publish:
  uv run dotenv --file pypi.env run uv publish dist/biased-*
