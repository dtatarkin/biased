[default]
[group("just")]
list-recipes:
    @just --list

# Configure completion for the Bash shell
[group("just")]
[linux]
bash-completion:
    just --completions bash > ~/.bashrc.d/just.sh

# Selecting Recipes to Run With an Interactive Chooser
[group("just")]
fzf:
    @just --choose --chooser fzf

# Format justfiles
[group("just")]
format-justfiles:
    just --fmt --unstable
