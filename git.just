[group("git")]
git-push *args:
    git push --recurse-submodules=on-demand {{ args }}

[group("git")]
git-pull *args:
    git pull --recurse-submodules {{ args }}

# Returns exit code 0 if clean, 1 if there are changes
[group("git")]
ensure-git-clean:
    git diff-index --quiet HEAD --
