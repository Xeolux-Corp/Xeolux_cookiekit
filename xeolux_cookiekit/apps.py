from django.apps import AppConfig


class XeoluxCookieKitConfig(AppConfig):
    name = "xeolux_cookiekit"
    verbose_name = "Xeolux CookieKit"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # Vérification silencieuse de la compatibilité cachekit au démarrage
        try:
            from xeolux_cookiekit.conf import get_cookiekit_config  # noqa: F401
        except Exception:
            pass
