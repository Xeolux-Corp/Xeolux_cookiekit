"""
views.py — Vue publique /cookiekit/ pour la configuration du consentement.

Sécurité :
  - Connexion Django obligatoire (redirect vers /admin/login/)
  - Permission `view_cookiekitconfig` pour accéder
  - Permission `change_cookiekitconfig` pour modifier
  - Statut superuser NON pris en compte — permissions explicites uniquement.
"""

from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import render

from xeolux_cookiekit.models import CookieCategory, CookieKitConfig, CookieKitIntegration


# ── Permission helpers (pas de bypass superuser) ──────────────────────────────

def _check_perm(user, codename: str) -> bool:
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    if not user.is_authenticated or not user.is_active:
        return False
    try:
        ct = ContentType.objects.get_for_model(CookieKitConfig)
        perm = Permission.objects.get(content_type=ct, codename=codename)
        return (
            user.user_permissions.filter(pk=perm.pk).exists()
            or user.groups.filter(permissions__pk=perm.pk).exists()
        )
    except Permission.DoesNotExist:
        return False


def _has_cookiekit_permission(user) -> bool:
    return _check_perm(user, "view_cookiekitconfig")


def _has_cookiekit_change_permission(user) -> bool:
    return _check_perm(user, "change_cookiekitconfig")


# ── Champs configurables depuis le dashboard ──────────────────────────────────

_BOOL_FIELDS = {
    "enabled", "cookie_secure", "cookie_signing_enabled", "shadow",
}
_SCALAR_FIELDS = {
    "consent_version", "cookie_max_age_days", "cookie_samesite",
    "banner_position", "banner_layout",
    "background_color", "text_color", "primary_color", "primary_text_color",
    "secondary_color", "border_radius",
    "title", "message",
    "accept_all_label", "reject_all_label", "customize_label",
    "privacy_policy_url",
}


def _apply_config_fields(config: CookieKitConfig, data: dict) -> list:
    errors = []
    for field in _SCALAR_FIELDS:
        if field in data:
            value = data[field]
            if field == "cookie_max_age_days":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    errors.append(f"{field}: valeur numérique invalide")
                    continue
            setattr(config, field, value)
    for field in _BOOL_FIELDS:
        setattr(config, field, bool(data.get(field, False)))
    return errors


# ── Vue principale ────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def cookiekit_dashboard(request):
    if not _has_cookiekit_permission(request.user):
        raise PermissionDenied

    can_edit = _has_cookiekit_change_permission(request.user)

    # POST — API JSON
    if request.method == "POST":
        if not can_edit:
            return JsonResponse({"ok": False, "error": "Permission refusée"}, status=403)
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"ok": False, "error": "JSON invalide"}, status=400)

        action = body.get("action", "")

        if action == "save_config":
            config = CookieKitConfig.objects.filter(enabled=True).first()
            if not config:
                return JsonResponse({"ok": False, "error": "Aucune configuration active"}, status=404)
            errors = _apply_config_fields(config, body)
            if errors:
                return JsonResponse({"ok": False, "error": "; ".join(errors)}, status=400)
            try:
                config.full_clean()
                config.save()
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    msgs = "; ".join(v for vals in exc.message_dict.values() for v in vals)
                else:
                    msgs = str(exc)
                return JsonResponse({"ok": False, "error": msgs}, status=400)
            return JsonResponse({"ok": True})

        if action == "toggle_integration":
            intg_id = body.get("id")
            enabled = bool(body.get("enabled", False))
            updated = CookieKitIntegration.objects.filter(pk=intg_id).update(enabled=enabled)
            if not updated:
                return JsonResponse({"ok": False, "error": "Intégration introuvable"}, status=404)
            return JsonResponse({"ok": True})

        if action == "save_intg_config":
            intg_id = body.get("id")
            config_data = body.get("config", {})
            if not isinstance(config_data, dict):
                return JsonResponse({"ok": False, "error": "config doit être un objet JSON"}, status=400)
            updated = CookieKitIntegration.objects.filter(pk=intg_id).update(config=config_data)
            if not updated:
                return JsonResponse({"ok": False, "error": "Intégration introuvable"}, status=404)
            return JsonResponse({"ok": True})

        if action == "toggle_category":
            cat_id = body.get("id")
            enabled = bool(body.get("enabled", False))
            updated = CookieCategory.objects.filter(pk=cat_id, required=False).update(enabled=enabled)
            if not updated:
                return JsonResponse({"ok": False, "error": "Catégorie introuvable ou requise"}, status=404)
            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "error": "Action inconnue"}, status=400)

    # GET
    config = CookieKitConfig.objects.filter(enabled=True).first()
    integrations = CookieKitIntegration.objects.all().order_by("order", "slug")
    integrations_by_category: dict = {}
    for intg in integrations:
        cat = intg.get_category_display()
        integrations_by_category.setdefault(cat, []).append(intg)
    categories = CookieCategory.objects.all().order_by("order", "key")
    cachekit_status = _get_cachekit_status(config)

    color_fields: list = []
    if config:
        color_fields = [
            ("background_color", "Couleur de fond", config.background_color),
            ("text_color", "Couleur du texte", config.text_color),
            ("primary_color", "Couleur primaire (boutons)", config.primary_color),
            ("primary_text_color", "Texte bouton primaire", config.primary_text_color),
            ("secondary_color", "Couleur secondaire", config.secondary_color),
        ]

    ctx = {
        "config": config,
        "can_edit": can_edit,
        "color_fields": color_fields,
        "integrations": integrations,
        "integrations_by_category": integrations_by_category,
        "integrations_active_count": integrations.filter(enabled=True).count(),
        "integrations_total": integrations.count(),
        "categories": categories,
        "cachekit_status": cachekit_status,
        "page_title": "CookieKit — Configuration",
    }
    return render(request, "xeolux_cookiekit/dashboard.html", ctx)


# ── Statut CacheKit ───────────────────────────────────────────────────────────

def _get_cachekit_status(config) -> dict:
    import importlib.util
    result = {
        "installed": False,
        "key": config.cachekit_version_key if config else "cookies",
        "version": None,
        "error": None,
    }
    if importlib.util.find_spec("xeolux_cachekit") is None:
        result["error"] = "non_installed"
        return result
    result["installed"] = True
    if config and config.cachekit_enabled:
        try:
            from xeolux_cachekit import get_cache_version  # type: ignore[import]
            result["version"] = get_cache_version(result["key"])
        except ImportError:
            result["error"] = "no_get_cache_version"
        except Exception as exc:
            result["error"] = str(exc)[:100]
    return result
