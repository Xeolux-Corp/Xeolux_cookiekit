"""
conf.py — Logique de fusion de configuration pour xeolux_cookiekit.

Ordre de priorité :
  1. Defaults internes (defaults.py)
  2. settings.XEOLUX_COOKIEKIT  — seule clé requise : {"enabled": True/False}
  3. Configuration admin si disponible et active (priorité maximale)

Règle : Admin actif > settings.py > defaults internes.

La table admin peut ne pas exister (migrations non lancées) :
dans ce cas, on tombe silencieusement sur settings.py.

Conformité RGPD/CNIL :
  - cookie_max_age plafonné à 395 jours (13 mois) — limite CNIL.
  - Un warning est émis si cookie_secure=False en production.
  - Toutes les catégories non-nécessaires doivent rester opt-in.
"""

from __future__ import annotations

import copy
import logging
from typing import Any

from django.conf import settings

from xeolux_cookiekit.defaults import (
    CNIL_MAX_COOKIE_AGE_SECONDS,
    COOKIEKIT_DEFAULTS,
)

logger = logging.getLogger("xeolux_cookiekit")


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Fusionne récursivement `override` dans `base`.
    Les valeurs scalaires de `override` remplacent celles de `base`.
    Les dicts sont fusionnés récursivement.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _get_settings_config() -> dict:
    """
    Retourne la configuration depuis settings.XEOLUX_COOKIEKIT.

    Configuration minimale recommandée :
        XEOLUX_COOKIEKIT = {"enabled": True}
    """
    raw = getattr(settings, "XEOLUX_COOKIEKIT", {})
    # Support du format ultra-minimal : XEOLUX_COOKIEKIT = True / False
    if isinstance(raw, bool):
        return {"enabled": raw}
    return raw if isinstance(raw, dict) else {}


def _get_admin_config() -> dict | None:
    """
    Tente de récupérer la configuration depuis l'admin Django (CookieKitConfig).
    Retourne None si :
      - La table n'existe pas encore (migrations absentes)
      - Aucune config active n'est définie
      - Toute autre erreur de base de données
    """
    try:
        from xeolux_cookiekit.models import CookieKitConfig  # noqa: PLC0415

        config = CookieKitConfig.objects.filter(enabled=True).first()
        if config is None:
            return None
        return config.to_settings_dict()
    except Exception:
        # Table absente ou erreur DB : fallback silencieux
        return None


def _get_cachekit_version(version_key: str) -> str | None:
    """
    Tente de récupérer la version depuis xeolux_cachekit.
    Retourne None si le package n'est pas installé ou si la clé est absente.
    """
    try:
        from xeolux_cachekit import get_cache_version  # type: ignore[import]

        return get_cache_version(version_key)
    except (ImportError, Exception):
        return None


def _validate_rgpd(config: dict) -> None:
    """
    Valide les points de conformité RGPD/CNIL et émet des warnings si nécessaire.
    Ne lève jamais d'exception — uniquement des avertissements dans les logs.
    """
    # Durée maximale CNIL : 13 mois (395 jours)
    max_age = config.get("cookie_max_age", 0)
    if max_age > CNIL_MAX_COOKIE_AGE_SECONDS:
        logger.warning(
            "xeolux_cookiekit [RGPD]: cookie_max_age (%s s) dépasse la limite CNIL "
            "de 395 jours (%s s). Valeur plafonnée automatiquement.",
            max_age,
            CNIL_MAX_COOKIE_AGE_SECONDS,
        )
        config["cookie_max_age"] = CNIL_MAX_COOKIE_AGE_SECONDS

    # cookie_secure en production
    debug_mode = getattr(settings, "DEBUG", False)
    if not debug_mode and not config.get("cookie_secure", True):
        logger.warning(
            "xeolux_cookiekit [RGPD]: cookie_secure=False en production. "
            "Le cookie de consentement ne sera transmis que sur HTTP. "
            "Activez cookie_secure=True pour les environnements HTTPS."
        )

    # Vérifier qu'aucune catégorie non-nécessaire n'est required=True avec enabled=True
    # par configuration automatique (ce serait un pré-cochage illégal CNIL)
    for key, cat in config.get("categories", {}).items():
        if key == "necessary":
            continue
        if cat.get("required") and cat.get("enabled"):
            logger.warning(
                "xeolux_cookiekit [RGPD]: La catégorie '%s' est marquée required=True "
                "et enabled=True. Seule la catégorie 'necessary' peut être requise. "
                "Cela constitue un pré-cochage non conforme CNIL.",
                key,
            )


def get_cookiekit_config() -> dict[str, Any]:
    """
    Retourne la configuration fusionnée de xeolux_cookiekit.

    Fusion dans l'ordre :
      defaults internes → settings.py → admin (si applicable)

    Usage minimal dans settings.py :
      XEOLUX_COOKIEKIT = {"enabled": True}
    """
    # 1. Base : defaults internes
    config = copy.deepcopy(COOKIEKIT_DEFAULTS)

    # 2. Fusion settings.py (peut être {"enabled": True} seulement)
    user_settings = _get_settings_config()
    if user_settings:
        config = _deep_merge(config, user_settings)

    # 3. Déterminer la source de configuration
    config_source = config.get("config_source", "admin_fallback_settings")

    if config_source == "settings_only":
        pass  # Admin ignoré
    elif config_source in ("admin_only", "admin_fallback_settings"):
        admin_config = _get_admin_config()
        if admin_config:
            config = _deep_merge(config, admin_config)
        elif config_source == "admin_only":
            logger.warning(
                "xeolux_cookiekit: config_source='admin_only' mais aucune "
                "CookieKitConfig active trouvée. Fallback sur defaults+settings."
            )

    # 4. Synchronisation cachekit (version)
    cachekit_conf = config.get("cachekit", {})
    if cachekit_conf.get("enabled") and cachekit_conf.get("sync_cookie_version"):
        version_key = cachekit_conf.get("version_key", "cookies")
        cachekit_version = _get_cachekit_version(version_key)
        if cachekit_version:
            config["consent_version"] = cachekit_version

    # 5. Validation RGPD (avec correction automatique si nécessaire)
    _validate_rgpd(config)

    return config

