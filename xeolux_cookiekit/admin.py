"""
admin.py — Interface d'administration Django pour xeolux_cookiekit.
"""

from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from xeolux_cookiekit.models import (
    CookieCategory,
    CookieKitConfig,
    CookieKitIntegration,
    CookieScript,
)


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
    readonly_fields = (
        "updated_at",
        "version_bump_hint",
        "analyticskit_bridge_status",
        "cachekit_version_status",
        "scripts_info",
        "integrations_info",
    )
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
        # ── Intégrations ───────────────────────────────────────────────────────
        (
            _("Intégrations tierces"),
            {
                "fields": ("integrations_info",),
                "description": _(
                    "Les intégrations (Google Analytics, Meta Pixel, Crisp, etc.) sont "
                    "gérées via le modèle dédié : Admin → Xeolux CookieKit → Intégrations."
                ),
            },
        ),
        # ── Scripts personnalisés ──────────────────────────────────────────────
        (
            _("Scripts personnalisés"),
            {
                "fields": ("scripts_info",),
                "description": _(
                    "Les scripts conditionnels sont gérés via le modèle CookieScript "
                    "(Admin → Xeolux CookieKit → Scripts personnalisés)."
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
                    "cachekit_version_status",
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

    @admin.display(description=_("🔌 Intégrations actives"))
    def integrations_info(self, obj: CookieKitConfig) -> str:
        """Affiche le résumé des intégrations actives et un lien de gestion."""
        try:
            total = CookieKitIntegration.objects.count()
            active = CookieKitIntegration.objects.filter(enabled=True).count()
            if active:
                names = ", ".join(
                    CookieKitIntegration.objects.filter(enabled=True)
                    .values_list("label", flat=True)[:5]
                )
                more = f" + {active - 5} autres" if active > 5 else ""
                return format_html(
                    '<span style="color:#22c55e;">✓ {} intégration(s) active(s)</span>'
                    ' — <span style="color:#888;">{}{}</span> / {} au total — '
                    '<a href="/admin/xeolux_cookiekit/cookiekitintegration/" '
                    'style="color:var(--xck-primary,#ff6b00)">Configurer les intégrations →</a>',
                    active,
                    names,
                    more,
                    total,
                )
            return format_html(
                '<span style="color:#f59e0b;">Aucune intégration active.</span> '
                '{} disponible(s) — '
                '<a href="/admin/xeolux_cookiekit/cookiekitintegration/" '
                'style="color:var(--xck-primary,#ff6b00)">Configurer les intégrations →</a>',
                total,
            )
        except Exception:
            return format_html(
                '<a href="/admin/xeolux_cookiekit/cookiekitintegration/">'
                "Configurer les intégrations →</a>"
            )

    @admin.display(description=_("📦 Statut CacheKit"))
    def cachekit_version_status(self, obj: CookieKitConfig) -> str:
        """Affiche la version cachekit résolue pour cette config."""
        import importlib.util

        if not obj.cachekit_enabled or not obj.cachekit_sync_cookie_version:
            return format_html('<span style="color:#888;">— Synchronisation désactivée</span>')

        # Étape 1 : vérifier si le module est installé (sans importer)
        if importlib.util.find_spec("xeolux_cachekit") is None:
            return format_html(
                '<span style="color:#f59e0b;">⚠ xeolux-cachekit non installé</span>'
                ' — <span style="color:#888;">pip install xeolux-cachekit</span>'
            )

        # Étape 2 : le module est installé, tenter d'appeler get_cache_version
        key = obj.cachekit_version_key or "cookies"
        try:
            from xeolux_cachekit import get_cache_version  # type: ignore[import]
        except ImportError:
            # Installé mais get_cache_version n'existe pas à ce niveau
            try:
                import xeolux_cachekit as _ck  # type: ignore[import]
                available = [x for x in dir(_ck) if not x.startswith("_")]
                return format_html(
                    '<span style="color:#22c55e;">✓ xeolux-cachekit installé</span>'
                    ' — <span style="color:#f59e0b;">get_cache_version() introuvable.'
                    " Fonctions disponibles&nbsp;: {}</span>",
                    ", ".join(available[:8]) or "—",
                )
            except Exception:
                return format_html(
                    '<span style="color:#22c55e;">✓ xeolux-cachekit installé</span>'
                    ' — <span style="color:#f59e0b;">API incompatible (get_cache_version manquant)</span>'
                )

        try:
            version = get_cache_version(key)
            if version:
                return format_html(
                    '<span style="color:#22c55e;">✓ Version résolue : <strong>{}</strong></span>'
                    ' <span style="color:#888;">(clé : {})</span>',
                    version,
                    key,
                )
            return format_html(
                '<span style="color:#f59e0b;">⚠ Clé <strong>{}</strong> introuvable dans cachekit.</span>'
                " <span style=\"color:#888;\">Créez cette clé ou modifiez le champ"
                " «&nbsp;Clé de version CacheKit&nbsp;».</span>",
                key,
            )
        except Exception as exc:
            return format_html(
                '<span style="color:#22c55e;">✓ xeolux-cachekit installé</span>'
                ' — <span style="color:#f59e0b;">Erreur get_cache_version({}) : {}</span>',
                key,
                str(exc)[:80],
            )

    @admin.display(description=_("📄 Scripts personnalisés"))
    def scripts_info(self, obj: CookieKitConfig) -> str:
        """Affiche le nombre de scripts actifs et un lien vers le modèle."""
        try:
            total = CookieScript.objects.count()
            active = CookieScript.objects.filter(enabled=True).count()
            return format_html(
                '<span style="color:#22c55e;">{} script(s) actif(s)</span>'
                " / {} au total — "
                '<a href="/admin/xeolux_cookiekit/cookiescript/" '
                'style="color:var(--xck-primary,#ff6b00)">Gérer les scripts →</a>',
                active,
                total,
            )
        except Exception:
            return format_html(
                '<a href="/admin/xeolux_cookiekit/cookiescript/">'
                "Gérer les scripts personnalisés →</a>"
            )

    @admin.display(description=_("💡 Bump de version"))
    def version_bump_hint(self, obj: CookieKitConfig) -> str:
        """Conseil affiché dans le formulaire pour incrémenter la version."""
        return format_html(
            '<span style="color:#888; font-size:0.9em;">'
            "Pour forcer le réaffichage du bandeau, modifiez manuellement le champ "
            "<strong>Version de consentement</strong> ci-dessus (ex&nbsp;: 1.0.0 → 1.1.0), "
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


@admin.register(CookieKitIntegration)
class CookieKitIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
        "enabled",
        "category",
        "config_summary",
        "order",
    )
    list_editable = ("enabled", "order")
    list_display_links = ("label",)
    list_filter = ("category", "enabled")
    search_fields = ("slug", "label")
    ordering = ("order", "slug")
    readonly_fields = ("slug", "config_help_display")
    actions = ["activate_integrations", "deactivate_integrations"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "slug",
                    "label",
                    "enabled",
                    "category",
                    "order",
                ),
            },
        ),
        (
            _("⚙ Configuration"),
            {
                "fields": (
                    "config_help_display",
                    "config",
                ),
                "description": _(
                    "Renseignez les paramètres de l'intégration au format JSON. "
                    "Consultez le champ d'aide ci-dessous pour connaître les clés attendues."
                ),
            },
        ),
    )

    def has_add_permission(self, request) -> bool:  # type: ignore[override]
        """Interdit l'ajout manuel d'intégrations — elles sont créées via post_migrate."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[override]
        """Interdit la suppression d'intégrations."""
        return False

    @admin.action(description=_("✅ Activer les intégrations sélectionnées"))
    def activate_integrations(self, request, queryset) -> None:
        count = queryset.update(enabled=True)
        self.message_user(
            request,
            _(f"✅ {count} intégration(s) activée(s)."),
            messages.SUCCESS,
        )

    @admin.action(description=_("❌ Désactiver les intégrations sélectionnées"))
    def deactivate_integrations(self, request, queryset) -> None:
        count = queryset.update(enabled=False)
        self.message_user(
            request,
            _(f"❌ {count} intégration(s) désactivée(s)."),
            messages.SUCCESS,
        )

    @admin.display(description=_("Configuration"))
    def config_summary(self, obj: CookieKitIntegration) -> str:
        """Affiche un résumé compact de la config JSON."""
        if not obj.config:
            return format_html('<span style="color:#888;">—</span>')
        keys = list(obj.config.keys())
        filled = [k for k in keys if obj.config.get(k)]
        if not filled:
            return format_html('<span style="color:#f59e0b;">⚠ Config vide</span>')
        return format_html(
            '<span style="color:#22c55e;">✓</span> {}',
            ", ".join(f"{k}=…" for k in filled[:3]) + ("…" if len(filled) > 3 else ""),
        )

    @admin.display(description=_("📋 Aide à la configuration"))
    def config_help_display(self, obj: CookieKitIntegration) -> str:
        """Affiche les champs JSON attendus pour cette intégration."""
        help_text = obj.get_config_help()
        lines = help_text.replace("\n", "<br>")
        return format_html(
            '<div style="background:#1a1a1a;color:#ccc;padding:12px 16px;border-radius:8px;'
            'font-family:monospace;font-size:0.85em;white-space:pre-wrap;line-height:1.6;">'
            "{}</div>",
            format_html(lines),
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


class CookieScriptAdminForm(forms.ModelForm):
    """
    Formulaire admin pour CookieScript.
    Le champ 'category' est un sélecteur dynamique alimenté par CookieCategory.
    """

    category = forms.ChoiceField(
        label=_("Catégorie de consentement requise"),
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cats = list(
            CookieCategory.objects.values_list("key", "label").order_by("order", "key")
        )
        if cats:
            self.fields["category"].choices = [
                (key, f"{label}  ({key})") for key, label in cats
            ]
        else:
            # Fallback si aucune catégorie en base (ex : migrate en cours)
            self.fields["category"].choices = [
                ("necessary", "Nécessaires  (necessary)"),
                ("analytics", "Mesure d'audience  (analytics)"),
                ("marketing", "Marketing  (marketing)"),
                ("preferences", "Préférences  (preferences)"),
            ]

    class Meta:
        model = CookieScript
        fields = "__all__"


@admin.register(CookieScript)
class CookieScriptAdmin(admin.ModelAdmin):
    form = CookieScriptAdminForm
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
