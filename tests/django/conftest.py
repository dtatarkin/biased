import django
from django.conf import settings


def pytest_configure(config):
    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        django.setup()
