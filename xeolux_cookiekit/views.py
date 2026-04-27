"""
views.py — Vue publique /cookiekit/ pour la gestion du consentement.

Sécurité :
  - Connexion Django obligatoire (redirect vers /admin/login/)
  - Permission `xeolux_cookiekit.view_cookiekitconfig` obligatoire
  - Le statut superuser N'est PAS pris en compte — la permission doit être
    explicitement attribuée à l'utilisateur ou à l'un de ses groupes.
  - Une tentative d'accès sans permission → 403 Forbidden.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from xeolux_cookiekit.models import CookieCategory, CookieKitConfig, CookieKitIntegration


# ──────────────────────────────────────────────────────────────────────────────
#  Vérification stricte de permission (pas de shortcut superuser)
# ──────────────────────────────────────────────────────────────────────────────

def _has_cookiekit_permission(user) -> bool:
    """
    Vérifie si l'utilisateur possède la permission view_cookiekitconfig
    SANS tenir compte du statut is_superuser.

    Contrairement à user.has_perm(), cette fonction vérifie directement
    les permissions assignées à l'utilisateur et à ses groupes.
    """
    from django.contrib.auth.models import Permission  # noqa: PLC0415
    from django.contrib.contenttypes.models import ContentType  # noqa: PLC0415

    if not user.is_authenticated or not user.is_active:
        return False

    try:
        ct = ContentType.objects.get_for_model(CookieKitConfig)
        perm = Permission.objects.get(content_type=ct, codename="view_cookiekitconfig")
        # Vérification directe : permissions utilisateur OU permissions de groupe
        return (
            user.user_permissions.filter(pk=perm.pk).exists()
            or user.groups.filter(permissions__pk=perm.pk).exists()
        )
    except Permission.DoesNotExist:
        return False


# ──────────────────────────────────────────────────────────────────────────────
#  Vue principale
# ──────────────────────────────────────────────────────────────────────────────

@login_required(login_url="/admin/login/")
def cookiekit_dashboard(request):
    """
    Tableau de bord simplifié pour la gestion du consentement cookies.

    Accessible à /cookiekit/. Requiert la permission view_cookiekitconfig.
    """
    if not _has_cookiekit_permission(request.user):
        raise PermissionDenied

    # ── Config principale ─────────────────────────────────────────────────────
    config = CookieKitConfig.objects.filter(enabled=True).first()

    # ── Intégrations regroupées par catégorie ─────────────────────────────────
    integrations = CookieKitIntegration.objects.all().order_by("order", "slug")
    integrations_by_category: dict = {}
    for intg in integrations:
        cat = intg.get_category_display()
        integrations_by_category.setdefault(cat, []).append(intg)

    # ── Catégories ────────────────────────────────────────────────────────────
    categories = CookieCategory.objects.all().order_by("order", "key")

    # ── Statut CacheKit ───────────────────────────────────────────────────────
    cachekit_status = _get_cachekit_status(config)

    ctx = {
        "config": config,
        "integrations": integrations,
        "integrations_by_category": integrations_by_category,
        "integrations_active_count": integrations.filter(enabled=True).count(),
        "integrations_total": integrations.count(),
        "categories": categories,
        "cachekit_status": cachekit_status,
        "page_title": "CookieKit — Gestion des cookies",
    }
    return render(request, "xeolux_cookiekit/dashboard.html", ctx)


def _get_cachekit_status(config) -> dict:
    """Retourne un dict de statut pour CacheKit."""
    import importlib.util  # noqa: PLC0415

    result = {
        "installed": False,
        "key": config.cachekit_version_key if config else "cookiekit",
        "version": None,
        "error": None,
    }

    if importlib.util.find_spec("xeolux_cachekit") is None:
        result["error"] = "non_installed"
        return result

    result["installed"] = True

    if config and config.cachekit_enabled:
        try:
            from xeolux_cachekit import get_version  # type: ignore[import]  # noqa: PLC0415

            result["version"] = get_version(result["key"])
        except ImportError:
            result["error"] = "no_get_version"
        except Exception as exc:
            result["error"] = str(exc)[:100]

    return result
