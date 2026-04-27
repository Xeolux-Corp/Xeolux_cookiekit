"""
conftest.py — Configuration pytest partagée.
"""
import django
from django.conf import settings


def pytest_configure():
    if not settings.configured:
        settings.configure(
            SECRET_KEY="xeolux-cookiekit-test-key",
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "xeolux_cookiekit",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            USE_TZ=True,
            XEOLUX_COOKIEKIT={
                "enabled": True,
                "consent_version": "1.0.0",
                "config_source": "settings_only",
                "style": {
                    "primary_color": "#ff6b00",
                },
            },
        )
