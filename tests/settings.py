"""
settings.py de test minimal pour pytest-django.
"""

SECRET_KEY = "xeolux-cookiekit-test-secret-key-not-for-production"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "xeolux_cookiekit",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

XEOLUX_COOKIEKIT = {
    "enabled": True,
    "consent_version": "1.0.0",
    "config_source": "settings_only",
    "style": {
        "primary_color": "#ff6b00",
    },
}
