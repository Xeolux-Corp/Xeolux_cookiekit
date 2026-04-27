"""
admin.py — Interface d'administration Django pour xeolux_cookiekit.
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from xeolux_cookiekit.models import CookieCategory, CookieKitConfig, CookieScript


@admin.register(CookieKitConfig)
class CookieKitConfigAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "enabled",
        "consent_version",
        "banner_position",
        "banner_layout",
        "analyticskit_bridge_enabled",
        "updated_at",
    )
    list_display_links = ("__str__",)
    readonly_fields = ("updated_at", "version_bump_hint", "analyticskit_bridge_status")
    actions = ["bump_patch_version"]

    fieldsets = (
        # ── Général ────────────────────────────────────────────────────────────
        (
            _("Général"),
            {
                "fields": (
                    "enabled",
                    "site_name",
                    "consent_version",
                    "version_bump_hint",
                    "cookie_name",
                    "cookie_max_age_days",
                    "cookie_secure",
                    "cookie_samesite",
                ),
            },
        ),
        # ── Sécurité du cookie ─────────────────────────────────────────────────
        (
            _("🔒 Sécurité du cookie"),
            {
                "fields": (
                    "cookie_signing_enabled",
                ),
                "description": _(
                    "La signature HMAC-SHA256 protège contre la falsification manuelle du cookie. "
                    "Un cookie supplémentaire HttpOnly (_sig) est posé côté serveur : "
                    "il n'est pas accessible au JavaScript et permet de détecter les altérations. "
                    "Désactiver uniquement si vous avez un proxy qui retire les cookies custom."
                ),
            },
        ),
        # ── Apparence ──────────────────────────────────────────────────────────
        (
            _("Apparence"),
            {
                "fields": (
                    "banner_position",
                    "banner_layout",
                    "background_color",
                    "text_color",
                    "primary_color",
                    "primary_text_color",
                    "secondary_color",
                    "secondary_text_color",
                    "border_radius",
                    "shadow",
                    "font_family",
                ),
                "classes": ("collapse",),
            },
        ),
        # ── Textes ─────────────────────────────────────────────────────────────
        (
            _("Textes"),
            {
                "fields": (
                    "title",
                    "message",
                    "accept_all_label",
                    "reject_all_label",
                    "customize_label",
                    "save_label",
                    "close_label",
                    "preferences_title",
                    "privacy_policy_label",
                    "privacy_policy_url",
                ),
                "classes": ("collapse",),
            },
        ),
        # ── Intégrations Google ────────────────────────────────────────────────
        (
            _("Intégrations Google"),
            {
                "fields": (
                    "google_analytics_enabled",
                    "google_analytics_id",
                    "google_tag_manager_enabled",
                    "google_tag_manager_id",
                ),
                "classes": ("collapse",),
            },
        ),
        # ── Autres intégrations ────────────────────────────────────────────────
        (
            _("Autres intégrations"),
            {
                "fields": (
                    "meta_pixel_enabled",
                    "meta_pixel_id",
                    "matomo_enabled",
                    "matomo_site_id",
                    "matomo_tracker_url",
                    "plausible_enabled",
                    "plausible_domain",
                    "linkedin_insight_enabled",
                    "linkedin_partner_id",
                    "tiktok_pixel_enabled",
                    "tiktok_pixel_id",
                    "twitter_pixel_enabled",
                    "twitter_pixel_id",
                    "clarity_enabled",
                    "clarity_project_id",
                    "hotjar_enabled",
                    "hotjar_site_id",
                    "crisp_enabled",
                    "crisp_website_id",
                ),
                "classes": ("collapse",),
            },
        ),
        # ── Scripts personnalisés ──────────────────────────────────────────────
        (
            _("Scripts personnalisés"),
            {
                "fields": (
                    "custom_head_scripts",
                    "custom_body_scripts",
                ),
                "classes": ("collapse",),
                "description": _(
                    "Ces scripts sont injectés après consentement. "
                    "Pour un contrôle fin par catégorie, utilisez le modèle CookieScript."
                ),
            },
        ),
        # ── CacheKit / Versioning ──────────────────────────────────────────────
        (
            _("CacheKit / Versioning"),
            {
                "fields": (
                    "cachekit_enabled",
                    "cachekit_sync_cookie_version",
                    "cachekit_version_key",
                ),
                "classes": ("collapse",),
            },
        ),
        # ── AnalyticsKit (intégration future) ─────────────────────────────────
        (
            _("AnalyticsKit (intégration future)"),
            {
                "fields": (
                    "analyticskit_bridge_enabled",
                    "analyticskit_bridge_status",
                ),
                "classes": ("collapse",),
                "description": _(
                    "Prépare l'intégration avec xeolux-analyticskit. "
                    "Installez 'pip install xeolux-analyticskit' pour activer le bridge."
                ),
            },
        ),
        # ── Avancé ────────────────────────────────────────────────────────────
        (
            _("Avancé"),
            {
                "fields": (
                    "z_index",
                    "custom_css",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("💡 Bump de version"))
    def version_bump_hint(self, obj: CookieKitConfig) -> str:
        """Conseil affiché dans le formulaire pour incrémenter la version."""
        return format_html(
            '<span style="color:#888; font-size:0.9em;">'
            "Pour forcer le réaffichage du bandeau, modifiez manuellement le champ "
            '<strong>Version de consentement</strong> ci-dessus (ex&nbsp;: 1.0.0 → 1.1.0), '
            "ou utilisez l'action <em>Incrémenter la version (patch)</em> depuis la liste."
            "</span>"
        )

    @admin.display(description=_("🔗 Statut Bridge AnalyticsKit"))
    def analyticskit_bridge_status(self, obj: CookieKitConfig) -> str:
        """Affiche l'état de disponibilité du bridge analyticskit."""
        try:
            from xeolux_cookiekit.analyticskit_bridge import get_bridge_status

            status = get_bridge_status()
            if status["analyticskit_available"]:
                handlers = status["handlers_count"]
                return format_html(
                    '<span style="color:#22c55e;">✓ xeolux-analyticskit installé</span>'
                    ' — <span style="color:#888;">{} handler(s) enregistré(s)</span>',
                    handlers,
                )
            else:
                return format_html(
                    '<span style="color:#f59e0b;">⚠ xeolux-analyticskit non installé</span>'
                    ' — <span style="color:#888;">pip install xeolux-analyticskit</span>'
                )
        except Exception:
            return format_html('<span style="color:#888;">—</span>')

    @admin.action(description=_("Incrémenter la version de consentement (patch +1)"))
    def bump_patch_version(
        self, request, queryset  # type: ignore[override]
    ) -> None:
        """
        Action admin : incrémente le patch de la version sémantique.
        Ex : 1.0.3 → 1.0.4
        """
        updated = 0
        for config in queryset:
            try:
                parts = config.consent_version.split(".")
                if len(parts) == 3:  # noqa: PLR2004
                    parts[2] = str(int(parts[2]) + 1)
                    config.consent_version = ".".join(parts)
                else:
                    config.consent_version = config.consent_version + ".1"
                config.save(update_fields=["consent_version", "updated_at"])
                updated += 1
            except (ValueError, TypeError):
                self.message_user(
                    request,
                    _(f"Impossible d'incrémenter la version de : {config}"),
                    level=messages.WARNING,
                )
        if updated:
            self.message_user(
                request,
                _(
                    f"{updated} configuration(s) mise(s) à jour. "
                    "Le bandeau réapparaîtra pour tous les visiteurs."
                ),
                level=messages.SUCCESS,
            )


@admin.register(CookieCategory)
class CookieCategoryAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "required", "enabled", "order")
    list_editable = ("enabled", "order")
    list_display_links = ("key",)
    ordering = ("order", "key")
    fieldsets = (
        (
            None,
            {
                "fields": ("key", "label", "description", "required", "enabled", "order"),
            },
        ),
    )


@admin.register(CookieScript)
class CookieScriptAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "position", "enabled", "order")
    list_editable = ("enabled", "order")
    list_display_links = ("name",)
    list_filter = ("position", "category", "enabled")
    ordering = ("position", "order", "name")
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "category", "enabled", "position", "order"),
            },
        ),
        (
            _("Code"),
            {
                "fields": ("script",),
            },
        ),
    )
