[group("git")]
git-push *args:
    git push --recurse-submodules=on-demand {{ args }}

[group("git")]
git-pull *args:
    git pull --recurse-submodules {{ args }}
