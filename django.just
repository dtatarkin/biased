[group("django")]
django-shell *args:
    pdm run python manage.py shell {{ args }}

[group("django")]
dbshell *args:
    pdm run python manage.py dbshell {{ args }}

[group("django")]
makemigrations *args:
    pdm run python manage.py makemigrations {{ args }}

[group("django")]
createsuperuser *args:
    pdm run python manage.py createsuperuser {{ args }}

[group("django")]
showurls *args:
    python manage.py show_urls {{ args }}
