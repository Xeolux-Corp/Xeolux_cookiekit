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

from xeolux_cookiekit.models import CookieCategory, CookieKitConfig, CookieKitIntegration, CookieScript


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
    "banner_backdrop_blur", "banner_overlay",
}
_SCALAR_FIELDS = {
    "consent_version", "cookie_max_age_days", "cookie_samesite",
    "banner_position", "banner_layout", "banner_color_scheme", "banner_animation",
    "dashboard_theme",
    # Palette sombre
    "background_color", "text_color", "primary_color", "primary_text_color",
    "secondary_color", "secondary_text_color", "banner_border_color",
    # Palette claire
    "light_background_color", "light_text_color", "light_primary_color",
    "light_primary_text_color", "light_secondary_color", "light_secondary_text_color",
    "light_border_color",
    # Options avancées bandeau
    "border_radius", "banner_border_radius_mobile",
    "banner_max_width", "banner_font_size", "banner_padding",
    "font_family", "z_index",
    # Textes
    "title", "message",
    "accept_all_label", "reject_all_label", "customize_label",
    "save_label", "close_label", "preferences_title", "privacy_policy_label",
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

        if action == "save_script":
            # Créer ou modifier un CookieScript
            script_id = body.get("id")
            name = str(body.get("name", "")).strip()
            category = str(body.get("category", "analytics")).strip()
            position = str(body.get("position", "head")).strip()
            script_code = str(body.get("script", "")).strip()
            order = int(body.get("order", 0))
            enabled = bool(body.get("enabled", True))
            if not name:
                return JsonResponse({"ok": False, "error": "Nom requis"}, status=400)
            if position not in ("head", "body"):
                return JsonResponse({"ok": False, "error": "Position invalide"}, status=400)
            if script_id:
                updated = CookieScript.objects.filter(pk=script_id).update(
                    name=name, category=category, position=position,
                    script=script_code, order=order, enabled=enabled,
                )
                if not updated:
                    return JsonResponse({"ok": False, "error": "Script introuvable"}, status=404)
                return JsonResponse({"ok": True, "id": script_id})
            else:
                obj = CookieScript.objects.create(
                    name=name, category=category, position=position,
                    script=script_code, order=order, enabled=enabled,
                )
                return JsonResponse({"ok": True, "id": obj.pk})

        if action == "toggle_script":
            script_id = body.get("id")
            enabled = bool(body.get("enabled", False))
            updated = CookieScript.objects.filter(pk=script_id).update(enabled=enabled)
            if not updated:
                return JsonResponse({"ok": False, "error": "Script introuvable"}, status=404)
            return JsonResponse({"ok": True})

        if action == "delete_script":
            script_id = body.get("id")
            deleted, _ = CookieScript.objects.filter(pk=script_id).delete()
            if not deleted:
                return JsonResponse({"ok": False, "error": "Script introuvable"}, status=404)
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
    custom_scripts = CookieScript.objects.all().order_by("position", "order", "name")
    cachekit_status = _get_cachekit_status(config)

    # Version de consentement résolue (CacheKit en priorité si sync active)
    resolved_consent_version = None
    if (
        config
        and config.cachekit_enabled
        and config.cachekit_sync_cookie_version
        and cachekit_status.get("version")
    ):
        resolved_consent_version = cachekit_status["version"]
    elif config:
        resolved_consent_version = config.consent_version

    color_fields: list = []
    light_color_fields: list = []
    if config:
        color_fields = [
            ("background_color", "Fond sombre", config.background_color),
            ("text_color", "Texte sombre", config.text_color),
            ("primary_color", "Primaire sombre", config.primary_color),
            ("primary_text_color", "Texte primaire sombre", config.primary_text_color),
            ("secondary_color", "Secondaire sombre", config.secondary_color),
            ("secondary_text_color", "Texte secondaire sombre", config.secondary_text_color),
        ]
        light_color_fields = [
            ("light_background_color", "Fond clair", config.light_background_color),
            ("light_text_color", "Texte clair", config.light_text_color),
            ("light_primary_color", "Primaire clair", config.light_primary_color),
            ("light_primary_text_color", "Texte primaire clair", config.light_primary_text_color),
            ("light_secondary_color", "Secondaire clair", config.light_secondary_color),
            ("light_secondary_text_color", "Texte secondaire clair", config.light_secondary_text_color),
        ]

    ctx = {
        "config": config,
        "can_edit": can_edit,
        "color_fields": color_fields,
        "light_color_fields": light_color_fields,
        "resolved_consent_version": resolved_consent_version,
        "integrations": integrations,
        "integrations_by_category": integrations_by_category,
        "integrations_active_count": integrations.filter(enabled=True).count(),
        "integrations_total": integrations.count(),
        "categories": categories,
        "custom_scripts": custom_scripts,
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
