"""
Valeurs par défaut internes de xeolux_cookiekit.
Ces valeurs sont la base de la fusion de configuration.

Règle de conformité RGPD / CNIL :
  - Seuls les cookies "nécessaires" sont actifs par défaut.
  - Toutes les autres catégories (analytics, marketing…) sont opt-in (enabled: False).
  - La durée maximale des cookies de consentement est de 13 mois (395 jours) selon la CNIL.
  - Le lien vers la politique de confidentialité est géré uniquement via l'admin Django.
  - L'URL de la politique de cookies NE DOIT PAS figurer dans settings.py pour éviter
    tout contournement de la revue juridique.

Configuration minimale settings.py recommandée :
    XEOLUX_COOKIEKIT = {"enabled": True}
    → Tout le reste est configuré via l'admin Django.
"""

from __future__ import annotations

# Durée maximale autorisée par la CNIL : 13 mois = 395 jours
CNIL_MAX_COOKIE_AGE_DAYS: int = 395
CNIL_MAX_COOKIE_AGE_SECONDS: int = CNIL_MAX_COOKIE_AGE_DAYS * 24 * 60 * 60

COOKIEKIT_DEFAULTS: dict = {
    # ── Activation ─────────────────────────────────────────────────────────
    # Seule clé attendue dans settings.py. Tout le reste se configure via admin.
    "enabled": True,

    # ── Source de configuration ─────────────────────────────────────────────
    # "settings_only"           → ignore l'admin Django
    # "admin_only"              → admin obligatoire
    # "admin_fallback_settings" → admin en priorité, fallback settings (défaut)
    "config_source": "admin_fallback_settings",

    # ── Cookie de consentement ─────────────────────────────────────────────
    "consent_version": "1.0.0",
    "cookie_name": "xeolux_cookie_consent",
    # CNIL : 6 mois recommandés, 13 mois max autorisés
    "cookie_max_age": 180 * 24 * 60 * 60,
    "cookie_secure": True,
    "cookie_samesite": "Lax",
    # Sécurité : signature HMAC-SHA256 du cookie via Django SECRET_KEY
    # Un cookie HttpOnly (_sig) est posé côté serveur pour détecter les falsifications.
    "cookie_signing_enabled": True,

    # ── Style du bandeau ───────────────────────────────────────────────────
    "style": {
        "position": "bottom",
        "layout": "banner",
        "theme": "xeolux",
        "background_color": "#111111",
        "text_color": "#ffffff",
        "primary_color": "#ff6b00",
        "primary_text_color": "#ffffff",
        "secondary_color": "#2b2b2b",
        "secondary_text_color": "#ffffff",
        "border_radius": "14px",
        "shadow": True,
        "font_family": "system",
        "z_index": 9999,
        "custom_css": "",
    },

    # ── Textes ─────────────────────────────────────────────────────────────
    "texts": {
        "title": "Gestion des cookies",
        "message": (
            "Nous utilisons des cookies pour améliorer votre expérience, "
            "mesurer l'audience et personnaliser certains contenus."
        ),
        "accept_all": "Tout accepter",
        "reject_all": "Tout refuser",
        "customize": "Personnaliser",
        "save": "Enregistrer mes choix",
        "close": "Fermer",
        "preferences_title": "Préférences cookies",
        "privacy_policy": "Politique de confidentialité",
    },

    # ── Catégories de cookies ──────────────────────────────────────────────
    # RGPD/CNIL : seules les cookies "nécessaires" peuvent être pré-activés.
    # Toutes les autres catégories DOIVENT être opt-in (enabled: False).
    "categories": {
        "necessary": {
            "label": "Nécessaires",
            "description": "Indispensables au fonctionnement du site.",
            "required": True,
            "enabled": True,   # Toujours actif — ne peut pas être refusé
        },
        "analytics": {
            "label": "Mesure d'audience",
            "description": "Nous aide à comprendre l'utilisation du site.",
            "required": False,
            "enabled": False,  # CNIL : opt-in obligatoire
        },
        "marketing": {
            "label": "Marketing",
            "description": "Permet d'activer les pixels publicitaires.",
            "required": False,
            "enabled": False,  # CNIL : opt-in obligatoire
        },
        "preferences": {
            "label": "Préférences",
            "description": "Permet de mémoriser certains choix d'interface.",
            "required": False,
            "enabled": False,  # CNIL : opt-in obligatoire
        },
    },

    # ── Intégrations tierces ───────────────────────────────────────────────
    "integrations": {
        "google_analytics": {
            "enabled": False,
            "measurement_id": "",
            "category": "analytics",
        },
        "google_tag_manager": {
            "enabled": False,
            "container_id": "",
            "category": "analytics",
        },
        "meta_pixel": {
            "enabled": False,
            "pixel_id": "",
            "category": "marketing",
        },
        "matomo": {
            "enabled": False,
            "site_id": "",
            "tracker_url": "",
            "category": "analytics",
        },
        "plausible": {
            "enabled": False,
            "domain": "",
            "script_url": "https://plausible.io/js/script.js",
            "category": "analytics",
        },
        "linkedin_insight": {
            "enabled": False,
            "partner_id": "",
            "category": "marketing",
        },
        "tiktok_pixel": {
            "enabled": False,
            "pixel_id": "",
            "category": "marketing",
        },
        "twitter_pixel": {
            "enabled": False,
            "pixel_id": "",
            "category": "marketing",
        },
        "clarity": {
            "enabled": False,
            "project_id": "",
            "category": "analytics",
        },
        "hotjar": {
            "enabled": False,
            "site_id": "",
            "category": "analytics",
        },
        "crisp": {
            "enabled": False,
            "website_id": "",
            "category": "preferences",
        },
    },

    # ── Compatibilité xeolux-cachekit ──────────────────────────────────────
    "cachekit": {
        "enabled": True,
        "sync_cookie_version": True,
        "version_key": "cookiekit",
    },

    # ── Intégration future xeolux-analyticskit ─────────────────────────────
    # Ce bloc est réservé pour la future intégration avec xeolux-analyticskit.
    # Il est ignoré si analyticskit n'est pas installé.
    "analyticskit": {
        "enabled": False,         # Activé automatiquement si analyticskit détecté
        "forward_consent": True,  # Transmet les changements de consentement à analyticskit
        "event_prefix": "xck",   # Préfixe des événements forwarded
    },

    "debug": False,
}
