"""
models.py — Modèles Django pour xeolux_cookiekit.

  - CookieKitConfig       : configuration globale singleton du bandeau
  - CookieKitIntegration  : intégrations tierces (analytics, marketing, chat…)
  - CookieCategory        : catégories de cookies configurables
  - CookieScript          : scripts personnalisés par catégorie
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# Limite CNIL : 13 mois = 395 jours
_CNIL_MAX_DAYS: int = 395


class CookieKitConfig(models.Model):
    """
    Configuration globale du bandeau cookies.
    Singleton logique : une seule instance active à la fois.
    """

    # --- Général ---
    enabled = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Si désactivé, le bandeau n'est pas affiché et settings.py est utilisé."),
    )
    site_name = models.CharField(
        _("Nom du site"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Utilisé dans les labels si besoin."),
    )
    consent_version = models.CharField(
        _("Version de consentement"),
        max_length=50,
        default="1.0.0",
        help_text=_(
            "Modifier cette valeur force le réaffichage du bandeau pour tous les visiteurs."
        ),
    )
    cookie_name = models.CharField(
        _("Nom du cookie"),
        max_length=100,
        default="xeolux_cookie_consent",
    )
    cookie_max_age_days = models.PositiveIntegerField(
        _("Durée du cookie (jours)"),
        default=180,
        help_text=_(
            "CNIL : 6 mois recommandés, 13 mois maximum autorisés (395 jours)."
        ),
    )
    cookie_secure = models.BooleanField(
        _("Cookie Secure"),
        default=True,
        help_text=_("Envoie le cookie uniquement sur HTTPS."),
    )
    cookie_samesite = models.CharField(
        _("Cookie SameSite"),
        max_length=10,
        default="Lax",
        choices=[("Lax", "Lax"), ("Strict", "Strict"), ("None", "None")],
    )

    # --- Apparence ---
    banner_position = models.CharField(
        _("Position du bandeau"),
        max_length=20,
        default="bottom",
        choices=[
            ("bottom", _("Bas de page")),
            ("top", _("Haut de page")),
            ("bottom-left", _("Bas gauche")),
            ("bottom-right", _("Bas droite")),
        ],
    )
    banner_layout = models.CharField(
        _("Layout"),
        max_length=20,
        default="banner",
        choices=[
            ("banner", _("Bandeau")),
            ("modal", _("Modal centré")),
            ("floating", _("Flottant")),
        ],
    )
    background_color = models.CharField(
        _("Couleur de fond"),
        max_length=20,
        default="#111111",
    )
    text_color = models.CharField(
        _("Couleur du texte"),
        max_length=20,
        default="#ffffff",
    )
    primary_color = models.CharField(
        _("Couleur primaire (boutons)"),
        max_length=20,
        default="#ff6b00",
    )
    primary_text_color = models.CharField(
        _("Texte bouton primaire"),
        max_length=20,
        default="#ffffff",
    )
    secondary_color = models.CharField(
        _("Couleur secondaire"),
        max_length=20,
        default="#2b2b2b",
    )
    secondary_text_color = models.CharField(
        _("Texte bouton secondaire"),
        max_length=20,
        default="#ffffff",
    )
    border_radius = models.CharField(
        _("Border radius"),
        max_length=20,
        default="14px",
    )
    shadow = models.BooleanField(
        _("Ombre portée"),
        default=True,
    )
    font_family = models.CharField(
        _("Police"),
        max_length=100,
        default="system",
        help_text=_(
            'Valeur CSS pour font-family. Utilisez "system" pour la police système.'
        ),
    )
    z_index = models.PositiveIntegerField(
        _("Z-Index"),
        default=9999,
    )
    custom_css = models.TextField(
        _("CSS personnalisé"),
        blank=True,
        default="",
        help_text=_("CSS additionnel injecté dans la page."),
    )

    # --- Textes ---
    title = models.CharField(
        _("Titre"),
        max_length=255,
        default="Gestion des cookies",
    )
    message = models.TextField(
        _("Message"),
        default=(
            "Nous utilisons des cookies pour améliorer votre expérience, "
            "mesurer l'audience et personnaliser certains contenus."
        ),
    )
    accept_all_label = models.CharField(
        _("Bouton Tout accepter"),
        max_length=100,
        default="Tout accepter",
    )
    reject_all_label = models.CharField(
        _("Bouton Tout refuser"),
        max_length=100,
        default="Tout refuser",
    )
    customize_label = models.CharField(
        _("Bouton Personnaliser"),
        max_length=100,
        default="Personnaliser",
    )
    save_label = models.CharField(
        _("Bouton Enregistrer"),
        max_length=100,
        default="Enregistrer mes choix",
    )
    close_label = models.CharField(
        _("Bouton Fermer"),
        max_length=100,
        default="Fermer",
    )
    preferences_title = models.CharField(
        _("Titre modal préférences"),
        max_length=255,
        default="Préférences cookies",
    )
    privacy_policy_label = models.CharField(
        _("Libellé lien politique de confidentialité"),
        max_length=100,
        default="Politique de confidentialité",
    )
    privacy_policy_url = models.URLField(
        _("URL politique de confidentialité / cookies"),
        max_length=500,
        blank=True,
        default="",
        help_text=_(
            "Si renseigné, un lien est affiché dans le bandeau. "
            "Exemple : /politique-de-confidentialite/"
        ),
    )

    # --- Sécurité du cookie ---
    cookie_signing_enabled = models.BooleanField(
        _("Signature HMAC activée"),
        default=True,
        help_text=_(
            "Active la signature HMAC-SHA256 du cookie de consentement avec Django SECRET_KEY. "
            "Un cookie HttpOnly supplémentaire (_sig) est posé côté serveur pour détecter "
            "toute falsification. Recommandé : activé."
        ),
    )

    # --- CacheKit ---
    cachekit_enabled = models.BooleanField(
        _("CacheKit activé"),
        default=True,
    )
    cachekit_sync_cookie_version = models.BooleanField(
        _("Synchroniser version via CacheKit"),
        default=True,
    )
    cachekit_version_key = models.CharField(
        _("Clé de version CacheKit"),
        max_length=100,
        default="cookiekit",
    )

    # --- AnalyticsKit (intégration future) ---
    analyticskit_bridge_enabled = models.BooleanField(
        _("Bridge AnalyticsKit activé"),
        default=False,
        help_text=_(
            "Active le pont entre CookieKit et xeolux-analyticskit. "
            "xeolux-analyticskit doit être installé. Préparé pour intégration future."
        ),
    )

    # --- Méta ---
    updated_at = models.DateTimeField(
        _("Mis à jour le"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Configuration CookieKit")
        verbose_name_plural = _("Configuration CookieKit")

    def __str__(self) -> str:
        status = "✓ Actif" if self.enabled else "✗ Inactif"
        return f"CookieKit Config — v{self.consent_version} [{status}]"

    def clean(self) -> None:
        """Validation RGPD/CNIL + singleton logique."""
        # Singleton : une seule config active
        if self.enabled:
            qs = CookieKitConfig.objects.filter(enabled=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    _(
                        "Une configuration active existe déjà. "
                        "Désactivez-la avant d'en activer une autre."
                    )
                )

        # CNIL : durée maximale 13 mois (395 jours)
        if self.cookie_max_age_days > _CNIL_MAX_DAYS:
            raise ValidationError(
                _(
                    "La durée du cookie ne peut pas dépasser %(max)s jours (13 mois — limite CNIL). "
                    "Valeur saisie : %(value)s jours."
                ) % {"max": _CNIL_MAX_DAYS, "value": self.cookie_max_age_days}
            )

    def to_settings_dict(self) -> dict:
        """
        Convertit l'instance en dictionnaire compatible avec le format settings.py.
        Utilisé par conf.get_cookiekit_config() pour la fusion.
        Les intégrations sont lues depuis CookieKitIntegration.
        """
        # Charger les intégrations depuis le modèle dédié
        integrations: dict = {}
        try:
            for intg in CookieKitIntegration.objects.all():
                integrations[intg.slug] = {
                    "enabled": intg.enabled,
                    "category": intg.category,
                    **intg.config,
                }
        except Exception:
            pass

        return {
            "enabled": self.enabled,
            "consent_version": self.consent_version,
            "cookie_name": self.cookie_name,
            "cookie_max_age": self.cookie_max_age_days * 24 * 60 * 60,
            "cookie_secure": self.cookie_secure,
            "cookie_samesite": self.cookie_samesite,
            "cookie_signing_enabled": self.cookie_signing_enabled,
            "style": {
                "position": self.banner_position,
                "layout": self.banner_layout,
                "background_color": self.background_color,
                "text_color": self.text_color,
                "primary_color": self.primary_color,
                "primary_text_color": self.primary_text_color,
                "secondary_color": self.secondary_color,
                "secondary_text_color": self.secondary_text_color,
                "border_radius": self.border_radius,
                "shadow": self.shadow,
                "font_family": self.font_family,
                "z_index": self.z_index,
                "custom_css": self.custom_css,
            },
            "privacy_policy_url": self.privacy_policy_url,
            "texts": {
                "title": self.title,
                "message": self.message,
                "accept_all": self.accept_all_label,
                "reject_all": self.reject_all_label,
                "customize": self.customize_label,
                "save": self.save_label,
                "close": self.close_label,
                "preferences_title": self.preferences_title,
                "privacy_policy": self.privacy_policy_label,
            },
            "integrations": integrations,
            "cachekit": {
                "enabled": self.cachekit_enabled,
                "sync_cookie_version": self.cachekit_sync_cookie_version,
                "version_key": self.cachekit_version_key,
            },
            "analyticskit": {
                "enabled": self.analyticskit_bridge_enabled,
                "forward_consent": True,
                "event_prefix": "xck",
            },
        }


class CookieKitIntegration(models.Model):
    """
    Intégration tierce conditionnée au consentement.

    Chaque entrée correspond à un service externe (analytics, marketing, chat…).
    La configuration spécifique (IDs, URLs) est stockée dans le JSONField `config`.
    Les scripts JS sont générés par integrations.py via build_integration_js().

    Exemple : slug="google_analytics", config={"measurement_id": "G-XXXXXXX"}
    """

    CATEGORY_CHOICES = [
        ("analytics", _("Analytics")),
        ("marketing", _("Marketing")),
        ("preferences", _("Préférences / Chat")),
        ("necessary", _("Nécessaires")),
    ]

    slug = models.SlugField(
        _("Identifiant (slug)"),
        max_length=100,
        unique=True,
        help_text=_("Identifiant technique immuable. Ex : google_analytics, meta_pixel."),
    )
    label = models.CharField(
        _("Nom affiché"),
        max_length=100,
    )
    enabled = models.BooleanField(
        _("Actif"),
        default=False,
    )
    category = models.CharField(
        _("Catégorie de consentement"),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="analytics",
        help_text=_(
            "Détermine quel consentement est requis pour activer cette intégration."
        ),
    )
    config = models.JSONField(
        _("Configuration"),
        default=dict,
        blank=True,
        help_text=_(
            "Paramètres spécifiques au format JSON. "
            "Ex : {\"measurement_id\": \"G-XXXXXXXX\"} pour Google Analytics. "
            "Les clés attendues sont affichées dans le champ d'aide ci-dessous."
        ),
    )
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"),
        default=0,
    )

    class Meta:
        verbose_name = _("Intégration")
        verbose_name_plural = _("Intégrations")
        ordering = ["order", "slug"]

    def __str__(self) -> str:
        status = "✓" if self.enabled else "✗"
        return f"[{status}] {self.label} ({self.slug})"

    def get_config_help(self) -> str:
        """Retourne les champs de configuration attendus pour cette intégration."""
        from xeolux_cookiekit.integrations import INTEGRATION_CATALOG  # noqa: PLC0415

        info = INTEGRATION_CATALOG.get(self.slug)
        if not info:
            return _("Intégration inconnue — aucune aide disponible.")
        lines = [f"Champs attendus pour « {info['label']} » :"]
        for key, field in info.get("fields", {}).items():
            label = field.get("label", key)
            help_text = field.get("help", "")
            placeholder = field.get("placeholder", "")
            line = f"  • {key} ({label})"
            if help_text:
                line += f" — {help_text}"
            if placeholder:
                line += f" [ex : {placeholder}]"
            lines.append(line)
        return "\n".join(lines)


class CookieCategory(models.Model):
    """
    Catégorie de cookies configurable via l'admin.
    Permet d'ajouter des catégories personnalisées en plus des catégories intégrées.
    """

    key = models.SlugField(
        _("Clé (identifiant)"),
        max_length=50,
        unique=True,
        help_text=_("Identifiant unique utilisé en JS. Ex : analytics, marketing, custom_cat"),
    )
    label = models.CharField(
        _("Label affiché"),
        max_length=100,
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        default="",
    )
    required = models.BooleanField(
        _("Requis"),
        default=False,
        help_text=_("Si coché, l'utilisateur ne peut pas désactiver cette catégorie."),
    )
    enabled = models.BooleanField(
        _("Activé par défaut"),
        default=False,
    )
    order = models.PositiveSmallIntegerField(
        _("Ordre d'affichage"),
        default=0,
    )

    class Meta:
        verbose_name = _("Catégorie de cookies")
        verbose_name_plural = _("Catégories de cookies")
        ordering = ["order", "key"]

    def __str__(self) -> str:
        return f"{self.label} ({self.key})"


class CookieScript(models.Model):
    """
    Script personnalisé conditionné à une catégorie de cookies.
    Injecté en head ou body après consentement.
    """

    HEAD = "head"
    BODY = "body"
    POSITION_CHOICES = [
        (HEAD, _("<head>")),
        (BODY, _("<body>")),
    ]

    name = models.CharField(
        _("Nom du script"),
        max_length=255,
        help_text=_("Nom descriptif pour identification dans l'admin."),
    )
    category = models.CharField(
        _("Catégorie de consentement requise"),
        max_length=50,
        default="analytics",
        help_text=_(
            "Clé de catégorie (ex : analytics, marketing). "
            "Le script n'est injecté que si cette catégorie est consentie."
        ),
    )
    enabled = models.BooleanField(
        _("Actif"),
        default=True,
    )
    position = models.CharField(
        _("Position d'injection"),
        max_length=10,
        choices=POSITION_CHOICES,
        default=HEAD,
    )
    script = models.TextField(
        _("Code HTML/Script"),
        help_text=_("Code HTML complet (avec balises <script> si nécessaire)."),
    )
    order = models.PositiveSmallIntegerField(
        _("Ordre d'exécution"),
        default=0,
    )

    class Meta:
        verbose_name = _("Script personnalisé")
        verbose_name_plural = _("Scripts personnalisés")
        ordering = ["position", "order", "name"]

    def __str__(self) -> str:
        status = "✓" if self.enabled else "✗"
        return f"[{status}] {self.name} ({self.position} — {self.category})"
