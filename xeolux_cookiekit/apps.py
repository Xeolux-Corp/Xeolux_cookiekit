from django.apps import AppConfig


# Catégories par défaut créées automatiquement après chaque migration
_DEFAULT_CATEGORIES = [
    {
        "key": "necessary",
        "label": "Nécessaires",
        "description": "Indispensables au fonctionnement du site. Ne peuvent pas être désactivés.",
        "required": True,
        "enabled": True,
        "order": 0,
    },
    {
        "key": "analytics",
        "label": "Mesure d'audience",
        "description": "Nous aide à comprendre comment les visiteurs utilisent le site (pages vues, parcours, temps passé).",
        "required": False,
        "enabled": False,
        "order": 1,
    },
    {
        "key": "marketing",
        "label": "Marketing",
        "description": "Permet d'activer les pixels publicitaires (Meta, LinkedIn, TikTok…) pour les campagnes ciblées.",
        "required": False,
        "enabled": False,
        "order": 2,
    },
    {
        "key": "preferences",
        "label": "Préférences",
        "description": "Mémorise certains choix d'interface (langue, thème…) pour améliorer votre expérience.",
        "required": False,
        "enabled": False,
        "order": 3,
    },
]


class XeoluxCookieKitConfig(AppConfig):
    name = "xeolux_cookiekit"
    verbose_name = "Xeolux CookieKit"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django.db.models.signals import post_migrate

        post_migrate.connect(_create_default_categories, sender=self)
        post_migrate.connect(_create_default_integrations, sender=self)


def _create_default_categories(sender, **kwargs) -> None:
    """
    Crée les 4 catégories de cookies par défaut si elles n'existent pas encore.
    Appelé automatiquement après chaque `python manage.py migrate`.
    Les catégories existantes ne sont jamais écrasées.
    """
    try:
        from xeolux_cookiekit.models import CookieCategory  # noqa: PLC0415

        for cat_data in _DEFAULT_CATEGORIES:
            CookieCategory.objects.get_or_create(
                key=cat_data["key"],
                defaults={
                    "label": cat_data["label"],
                    "description": cat_data["description"],
                    "required": cat_data["required"],
                    "enabled": cat_data["enabled"],
                    "order": cat_data["order"],
                },
            )
    except Exception:
        # Silencieux si la table n'existe pas encore (migrations non appliquées)
        pass


def _create_default_integrations(sender, **kwargs) -> None:
    """
    Crée les intégrations par défaut depuis INTEGRATION_CATALOG si elles n'existent pas.
    Aucune intégration n'est activée par défaut (enabled=False).
    Les intégrations existantes ne sont jamais modifiées.
    Appelé automatiquement après chaque `python manage.py migrate`.
    """
    try:
        from xeolux_cookiekit.integrations import INTEGRATION_CATALOG  # noqa: PLC0415
        from xeolux_cookiekit.models import CookieKitIntegration  # noqa: PLC0415

        for slug, info in INTEGRATION_CATALOG.items():
            CookieKitIntegration.objects.get_or_create(
                slug=slug,
                defaults={
                    "label": info["label"],
                    "enabled": False,
                    "category": info["category"],
                    "config": {},
                    "order": info.get("order", 0),
                },
            )
    except Exception:
        # Silencieux si la table n'existe pas encore (migrations non appliquées)
        pass
