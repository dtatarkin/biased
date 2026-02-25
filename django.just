[group("django")]
django-shell *args:
    just manage shell {{ args }}

[group("django")]
dbshell *args:
    just manage dbshell {{ args }}

[group("django")]
makemigrations *args:
    just manage makemigrations {{ args }}

[group("django")]
createsuperuser *args:
    just manage createsuperuser {{ args }}

[group("django")]
showurls *args:
    just manage show_urls {{ args }}
