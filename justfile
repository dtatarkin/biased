default:
  @just --list

shell:
    uv venv --allow-existing 2>&1 | tail -n 1 | sed "s/Activate with: //"

bump-dev:
  uv version --bump dev

build:
  uv build

publish:
  dotenv --file pypi.env run uv publish dist/biased-*

system-info:
  @echo "This is an {{arch()}} machine".

executable:
  @echo The executable is at: {{just_executable()}}
