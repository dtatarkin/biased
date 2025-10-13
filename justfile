default:
  @just --list

bump-dev:
  uv version --bump dev

system-info:
  @echo "This is an {{arch()}} machine".

executable:
  @echo The executable is at: {{just_executable()}}
