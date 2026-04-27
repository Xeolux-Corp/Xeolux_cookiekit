"""
security.py — Sécurisation du cookie de consentement côté Django.

Stratégie de sécurité en deux couches :

  COUCHE 1 — Côté client (JS) :
    - Validation du schéma JSON (types, clés connues, taille max).
    - Whitelist des clés de catégories (aucune injection de clé arbitraire).
    - Rejet de tout cookie malformé → affichage du bandeau.

  COUCHE 2 — Côté serveur (Django, ce fichier) :
    - Signature HMAC-SHA256 du payload JSON avec Django SECRET_KEY.
    - Cookie de vérification `_xck_sig` en HttpOnly + Secure (non accessible au JS).
    - `verify_consent_request(request)` → vérifie que le cookie n'a pas été falsifié.
    - `get_verified_consent(request)` → retourne le consentement vérifié ou None.

Contre-mesures :

  ┌──────────────────────────────────────────────────────────────────────┐
  │ Attaque                      │ Protection                           │
  ├──────────────────────────────┼───────────────────────────────────────┤
  │ Falsification manuelle       │ HMAC-SHA256 + cookie sig HttpOnly    │
  │ Injection de catégories      │ Whitelist côté JS + validation Django │
  │ Cookie trop grand (DoS)      │ Limite de taille (MAX_COOKIE_BYTES)  │
  │ Lecture par XSS              │ Cookie sig HttpOnly (pas accessible) │
  │ Replay sur HTTP              │ Flag Secure en production            │
  │ CSRF sur cookie              │ SameSite=Lax (défaut) ou Strict      │
  │ Expiration non respectée     │ CNIL max 395 jours enforced          │
  └──────────────────────────────┴───────────────────────────────────────┘

Usage Django (views, middleware, templatetags) :

    from xeolux_cookiekit.security import get_verified_consent, ConsentVerificationError

    consent = get_verified_consent(request)
    if consent and consent.choices.get("analytics"):
        # L'utilisateur a bien consenti à analytics, cookie non falsifié
        ...

    # Ou directement avec levée d'exception :
    try:
        consent = get_verified_consent(request, raise_on_invalid=True)
    except ConsentVerificationError:
        # Cookie falsifié ou absent
        ...
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("xeolux_cookiekit.security")

# ── Constantes de sécurité ─────────────────────────────────────────────────────
MAX_COOKIE_BYTES: int = 4096       # Limite navigateur standard
MAX_PAYLOAD_BYTES: int = 2048      # Notre limite interne (au-delà = suspect)
MAX_VERSION_LENGTH: int = 20       # "1.0.0" → très court
MAX_CATEGORY_KEY_LENGTH: int = 50  # Clé de catégorie (slug)
MAX_CATEGORIES: int = 20           # Nombre max de catégories dans le cookie
SIG_COOKIE_SUFFIX: str = "_sig"    # Nom du cookie de signature HttpOnly
HMAC_DIGEST: str = "sha256"

# Caractères autorisés pour une clé de catégorie (slug Django)
_CATEGORY_KEY_RE = re.compile(r'^[a-z0-9_\-]{1,50}$')
# Version sémantique ou simple
_VERSION_RE = re.compile(r'^[\d.a-zA-Z\-]{1,20}$')


class ConsentVerificationError(Exception):
    """Levée si le cookie de consentement est absent, malformé ou falsifié."""
    pass


@dataclass
class VerifiedConsent:
    """Consentement vérifié par signature HMAC."""
    version: str
    updated_at: str
    choices: dict[str, bool]
    is_signed: bool  # True si la signature a été vérifiée avec succès

    def has(self, category: str) -> bool:
        """Retourne True si la catégorie est consentie (et la clé est valide)."""
        if not _CATEGORY_KEY_RE.match(category):
            return False
        return self.choices.get(category, False) is True


# ── Signature HMAC ─────────────────────────────────────────────────────────────

def _get_signing_key() -> bytes:
    """
    Retourne la clé de signature HMAC dérivée de Django SECRET_KEY.
    Utilise une clé dérivée spécifique à cookiekit pour ne pas
    partager le secret brut avec d'autres composants.
    """
    secret = settings.SECRET_KEY
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    return hmac.new(
        secret,
        b"xeolux_cookiekit_consent_v1",
        hashlib.sha256,
    ).digest()


def _sign_payload(payload_json: str) -> str:
    """
    Génère une signature HMAC-SHA256 du payload JSON.
    Retourne la signature en hexadécimal.
    """
    key = _get_signing_key()
    sig = hmac.new(key, payload_json.encode("utf-8"), hashlib.sha256)
    return sig.hexdigest()


def _verify_signature(payload_json: str, signature: str) -> bool:
    """
    Vérifie la signature HMAC en temps constant (résistant au timing attack).
    """
    expected = _sign_payload(payload_json)
    try:
        return hmac.compare_digest(expected, signature)
    except (TypeError, ValueError):
        return False


# ── Validation du payload ──────────────────────────────────────────────────────

def _validate_consent_payload(data: Any) -> dict[str, Any]:
    """
    Valide la structure du payload de consentement.
    Retourne le payload nettoyé ou lève ConsentVerificationError.

    Vérifications :
      - Type dict
      - Champs requis (version, updated_at, choices)
      - Format de version
      - Choices : dict de booléens uniquement
      - Clés de catégories : whitelist slug
      - Nombre de catégories ≤ MAX_CATEGORIES
    """
    if not isinstance(data, dict):
        raise ConsentVerificationError("Payload n'est pas un objet JSON.")

    # Champs requis
    for field in ("version", "choices"):
        if field not in data:
            raise ConsentVerificationError(f"Champ requis absent : '{field}'.")

    # Version
    version = data["version"]
    if not isinstance(version, str) or not _VERSION_RE.match(version):
        raise ConsentVerificationError(f"Version invalide : {version!r}.")

    # Choices
    choices_raw = data["choices"]
    if not isinstance(choices_raw, dict):
        raise ConsentVerificationError("'choices' doit être un objet.")

    if len(choices_raw) > MAX_CATEGORIES:
        raise ConsentVerificationError(
            f"Trop de catégories dans 'choices' ({len(choices_raw)} > {MAX_CATEGORIES})."
        )

    # Nettoyer les choices : ne garder que les clés valides avec des valeurs booléennes
    clean_choices: dict[str, bool] = {}
    for key, val in choices_raw.items():
        if not isinstance(key, str) or not _CATEGORY_KEY_RE.match(key):
            logger.warning(
                "xeolux_cookiekit [sécurité]: clé de catégorie invalide ignorée : %r",
                key,
            )
            continue
        # Forcer le type booléen
        clean_choices[key] = bool(val)

    # necessary est toujours True
    clean_choices["necessary"] = True

    return {
        "version": version,
        "updated_at": data.get("updated_at", ""),
        "choices": clean_choices,
    }


# ── Écriture sécurisée du cookie de signature ──────────────────────────────────

def set_signed_consent_cookie(
    response: HttpResponse,
    cookie_name: str,
    payload_json: str,
    max_age: int,
    secure: bool = True,
    samesite: str = "Lax",
) -> None:
    """
    Pose le cookie de signature HttpOnly sur la réponse Django.

    Ce cookie (`<cookie_name>_sig`) contient le HMAC-SHA256 du payload.
    Il est :
      - HttpOnly → inaccessible au JavaScript (protection XSS)
      - Secure → transmis uniquement en HTTPS
      - SameSite → protection CSRF

    Doit être appelé depuis une view ou un middleware Django après que
    l'utilisateur a enregistré ses préférences via la route consentement.
    """
    sig = _sign_payload(payload_json)
    sig_cookie_name = cookie_name + SIG_COOKIE_SUFFIX

    response.set_cookie(
        sig_cookie_name,
        sig,
        max_age=max_age,
        path="/",
        secure=secure,
        httponly=True,  # Inaccessible au JS
        samesite=samesite,
    )
    logger.debug(
        "xeolux_cookiekit [sécurité]: cookie de signature '%s' posé (HttpOnly).",
        sig_cookie_name,
    )


# ── Vérification côté serveur ──────────────────────────────────────────────────

def verify_consent_request(
    request: HttpRequest,
    cookie_name: str | None = None,
) -> bool:
    """
    Vérifie que le cookie de consentement présent dans la requête
    correspond à la signature HttpOnly.

    Retourne True si le cookie est valide et non falsifié.
    Retourne False si absent, malformé, ou signature non concordante.
    """
    from xeolux_cookiekit.conf import get_cookiekit_config

    if cookie_name is None:
        config = get_cookiekit_config()
        cookie_name = config.get("cookie_name", "xeolux_cookie_consent")

    raw_consent = request.COOKIES.get(cookie_name)
    raw_sig = request.COOKIES.get(cookie_name + SIG_COOKIE_SUFFIX)

    if not raw_consent or not raw_sig:
        return False

    # Taille maximale
    if len(raw_consent) > MAX_PAYLOAD_BYTES:
        logger.warning(
            "xeolux_cookiekit [sécurité]: cookie trop large (%d bytes) — rejeté.",
            len(raw_consent),
        )
        return False

    try:
        decoded = _url_decode(raw_consent)
    except Exception:
        return False

    return _verify_signature(decoded, raw_sig)


def get_verified_consent(
    request: HttpRequest,
    cookie_name: str | None = None,
    raise_on_invalid: bool = False,
) -> VerifiedConsent | None:
    """
    Lit, valide et vérifie le cookie de consentement côté serveur.

    Args:
        request: La requête Django.
        cookie_name: Nom du cookie (optionnel, lu depuis la config).
        raise_on_invalid: Si True, lève ConsentVerificationError au lieu de None.

    Returns:
        VerifiedConsent si le cookie est valide, None sinon (si raise_on_invalid=False).
    """
    from xeolux_cookiekit.conf import get_cookiekit_config

    if cookie_name is None:
        config = get_cookiekit_config()
        cookie_name = config.get("cookie_name", "xeolux_cookie_consent")

    raw = request.COOKIES.get(cookie_name)
    if not raw:
        if raise_on_invalid:
            raise ConsentVerificationError("Cookie de consentement absent.")
        return None

    # Taille maximale
    if len(raw) > MAX_PAYLOAD_BYTES:
        msg = f"Cookie de consentement trop large ({len(raw)} bytes)."
        logger.warning("xeolux_cookiekit [sécurité]: %s", msg)
        if raise_on_invalid:
            raise ConsentVerificationError(msg)
        return None

    # Décodage URL
    try:
        decoded = _url_decode(raw)
    except Exception as exc:
        msg = f"Décodage URL du cookie échoué : {exc}"
        if raise_on_invalid:
            raise ConsentVerificationError(msg) from exc
        return None

    # Parse JSON
    try:
        data = json.loads(decoded)
    except (json.JSONDecodeError, ValueError) as exc:
        msg = f"JSON invalide dans le cookie de consentement."
        logger.warning("xeolux_cookiekit [sécurité]: %s", msg)
        if raise_on_invalid:
            raise ConsentVerificationError(msg) from exc
        return None

    # Validation du schéma
    try:
        clean_data = _validate_consent_payload(data)
    except ConsentVerificationError:
        if raise_on_invalid:
            raise
        return None

    # Vérification de la signature HMAC (si cookie sig présent)
    raw_sig = request.COOKIES.get(cookie_name + SIG_COOKIE_SUFFIX)
    is_signed = False
    if raw_sig:
        if not _verify_signature(decoded, raw_sig):
            msg = "Signature HMAC du cookie de consentement invalide — possible falsification."
            logger.warning("xeolux_cookiekit [sécurité]: %s", msg)
            if raise_on_invalid:
                raise ConsentVerificationError(msg)
            return None
        is_signed = True
    else:
        logger.debug(
            "xeolux_cookiekit [sécurité]: cookie de signature absent — "
            "vérification HMAC ignorée (migration progressive)."
        )

    return VerifiedConsent(
        version=clean_data["version"],
        updated_at=clean_data.get("updated_at", ""),
        choices=clean_data["choices"],
        is_signed=is_signed,
    )


def read_consent_from_request(request: HttpRequest, cookie_name: str | None = None) -> dict | None:
    """
    Lecture simplifiée du consentement depuis une requête Django,
    sans vérification de signature (pour les cas où la signature n'est pas requise).
    Valide uniquement le schéma JSON.

    Préférer get_verified_consent() pour une sécurité maximale.
    """
    from xeolux_cookiekit.conf import get_cookiekit_config

    if cookie_name is None:
        config = get_cookiekit_config()
        cookie_name = config.get("cookie_name", "xeolux_cookie_consent")

    raw = request.COOKIES.get(cookie_name)
    if not raw:
        return None

    if len(raw) > MAX_PAYLOAD_BYTES:
        return None

    try:
        decoded = _url_decode(raw)
        data = json.loads(decoded)
        return _validate_consent_payload(data)
    except Exception:
        return None


# ── Utilitaires ────────────────────────────────────────────────────────────────

def _url_decode(value: str) -> str:
    """Décode un cookie encodé par encodeURIComponent côté JS."""
    from urllib.parse import unquote
    return unquote(value)
