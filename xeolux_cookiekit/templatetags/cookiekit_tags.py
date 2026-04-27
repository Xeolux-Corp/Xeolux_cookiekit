"""
cookiekit_tags.py — Template tags xeolux_cookiekit.

Tags disponibles :
  {% cookiekit_head %}          → CSS vars + scripts consentis (head)
  {% cookiekit_body %}          → noscript GTM + scripts consentis (body)
  {% cookiekit_banner %}        → Bandeau + modal préférences
  {% cookiekit_script "cat" %}…{% endcookiekit_script %}
                                → Script conditionné au consentement JS
"""

from __future__ import annotations

import json
import re

from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from xeolux_cookiekit.conf import get_cookiekit_config

register = template.Library()


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers internes
# ──────────────────────────────────────────────────────────────────────────────

def _safe_color(value: str) -> str:
    """Valide qu'une valeur CSS couleur ne contient pas de caractères dangereux."""
    if re.match(r'^[#a-zA-Z0-9(),.\s%]+$', value):
        return value
    return ""


def _font_family(value: str) -> str:
    """Retourne la déclaration CSS font-family."""
    if value == "system" or not value:
        return (
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
            "Oxygen, Ubuntu, sans-serif"
        )
    # Sanitize basique : pas d'injection CSS
    if re.match(r"^[a-zA-Z0-9 ,'\"-]+$", value):
        return value
    return "sans-serif"


def _build_css_vars(style: dict) -> str:
    """Génère les CSS custom properties depuis la config style."""
    shadow_val = (
        "0 8px 40px rgba(0,0,0,0.45)"
        if style.get("shadow")
        else "none"
    )
    z_index = int(style.get("z_index", 9999))
    radius = style.get("border_radius", "14px")
    if not re.match(r'^[\d.]+(%|px|em|rem|vw|vh)?$', str(radius)):
        radius = "14px"

    color_scheme = style.get("color_scheme", "dark")  # dark | light | auto

    # Couleurs configurées par l'utilisateur (utilisées uniquement en mode dark/custom)
    bg       = _safe_color(style.get("background_color", "#111111"))
    text     = _safe_color(style.get("text_color", "#ffffff"))
    primary  = _safe_color(style.get("primary_color", "#ff6b00"))
    p_text   = _safe_color(style.get("primary_text_color", "#ffffff"))
    sec      = _safe_color(style.get("secondary_color", "#2b2b2b"))
    sec_text = _safe_color(style.get("secondary_text_color", "#ffffff"))

    # Valeurs light prédéfinies (thème clair Apple-style)
    _LIGHT = {
        "bg": "#f5f5f7", "text": "#1d1d1f",
        "primary": "#e05e00", "primary_text": "#ffffff",
        "secondary": "#e0e0e5", "secondary_text": "#1d1d1f",
    }

    def _vars_block(scheme: str) -> list[str]:
        """Retourne les lignes de variables pour un schéma donné."""
        if scheme == "light":
            return [
                f"  --xck-bg: {_LIGHT['bg']};",
                f"  --xck-text: {_LIGHT['text']};",
                f"  --xck-primary: {_LIGHT['primary']};",
                f"  --xck-primary-text: {_LIGHT['primary_text']};",
                f"  --xck-secondary: {_LIGHT['secondary']};",
                f"  --xck-secondary-text: {_LIGHT['secondary_text']};",
            ]
        # dark : utilise les couleurs configurées par l'admin
        return [
            f"  --xck-bg: {bg};",
            f"  --xck-text: {text};",
            f"  --xck-primary: {primary};",
            f"  --xck-primary-text: {p_text};",
            f"  --xck-secondary: {sec};",
            f"  --xck-secondary-text: {sec_text};",
        ]

    common = [
        f"  --xck-radius: {radius};",
        f"  --xck-z-index: {z_index};",
        f"  --xck-shadow: {shadow_val};",
        f"  --xck-font: {_font_family(style.get('font_family', 'system'))};",
    ]

    if color_scheme == "light":
        lines = [":root {"] + _vars_block("light") + common + ["}"]
    elif color_scheme == "auto":
        # Mode auto : dark par défaut, light si prefers-color-scheme: light
        lines = (
            [":root {"] + _vars_block("dark") + common + ["}",
            "@media (prefers-color-scheme: light) {",
            "  :root {"] + _vars_block("light") + ["  }", "}"]
        )
    else:
        # dark (défaut)
        lines = [":root {"] + _vars_block("dark") + common + ["}"]

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  {% cookiekit_head %}
# ──────────────────────────────────────────────────────────────────────────────

@register.simple_tag
def cookiekit_head() -> SafeString:
    """
    Injecte dans le <head> :
      - Lien vers cookiekit.css
      - CSS variables inline
      - CSS personnalisé
      - Config JS globale
      - Script cookiekit.js
      - Scripts intégrations consentis (GA4, GTM, Matomo, Plausible, Meta Pixel)
      - Scripts head personnalisés (CookieScript + custom_head_scripts)
    """
    try:
        config = get_cookiekit_config()
    except Exception:
        return mark_safe("")

    if not config.get("enabled"):
        return mark_safe("")

    style = config.get("style", {})
    texts = config.get("texts", {})
    categories = config.get("categories", {})
    integrations = config.get("integrations", {})

    # ── CSS vars + static link ──────────────────────────────────────────────
    css_vars = _build_css_vars(style)
    custom_css = style.get("custom_css", "")

    # Catégories à transmettre au JS (depuis DB si dispo + settings)
    cats_from_db = _get_db_categories()
    merged_categories = {**categories, **cats_from_db}

    # Config JS sérialisée
    js_config = json.dumps(
        {
            "consent_version": config.get("consent_version", "1.0.0"),
            "cookie_name": config.get("cookie_name", "xeolux_cookie_consent"),
            "cookie_max_age": config.get("cookie_max_age", 180 * 24 * 60 * 60),
            "cookie_secure": config.get("cookie_secure", True),
            "cookie_samesite": config.get("cookie_samesite", "Lax"),
            "categories": merged_categories,
            "texts": texts,
            "style": {
                "position": style.get("position", "bottom"),
                "layout": style.get("layout", "banner"),
            },
            "debug": config.get("debug", False),
        },
        ensure_ascii=False,
    )

    # ── Intégrations conditionelles (injectées par JS après consentement) ──
    integrations_js = _build_integrations_js(integrations)

    # ── Scripts head custom (CookieScript model uniquement) ───────────────
    custom_scripts_html = _get_custom_scripts_html("head")

    parts = [
        f'<link rel="stylesheet" href="/static/xeolux_cookiekit/cookiekit.css">',
        f"<style>{css_vars}</style>",
    ]
    if custom_css:
        parts.append(f"<style>{custom_css}</style>")
    parts += [
        f"<script>window.__XCK_CONFIG__ = {js_config};</script>",
        f'<script src="/static/xeolux_cookiekit/cookiekit.js" defer></script>',
        integrations_js,
        custom_scripts_html,
    ]

    return mark_safe("\n".join(filter(None, parts)))


# ──────────────────────────────────────────────────────────────────────────────
#  {% cookiekit_body %}
# ──────────────────────────────────────────────────────────────────────────────

@register.simple_tag
def cookiekit_body() -> SafeString:
    """
    Injecte au début du <body> :
      - noscript GTM (si GTM activé)
      - Scripts body personnalisés (CookieScript + custom_body_scripts)
    """
    try:
        config = get_cookiekit_config()
    except Exception:
        return mark_safe("")

    if not config.get("enabled"):
        return mark_safe("")

    parts = []
    integrations = config.get("integrations", {})

    # GTM noscript (body fallback)
    gtm = integrations.get("google_tag_manager", {})
    if gtm.get("enabled"):
        from xeolux_cookiekit.integrations import get_gtm_noscript  # noqa: PLC0415

        noscript = get_gtm_noscript(gtm)
        if noscript:
            parts.append(noscript)

    # Scripts body personnalisés (model uniquement)
    parts.append(_get_custom_scripts_html("body"))

    return mark_safe("\n".join(filter(None, parts)))


# ──────────────────────────────────────────────────────────────────────────────
#  {% cookiekit_banner %}
# ──────────────────────────────────────────────────────────────────────────────

@register.inclusion_tag("xeolux_cookiekit/banner.html")
def cookiekit_banner() -> dict:
    """Affiche le bandeau cookies + la modal de préférences."""
    try:
        config = get_cookiekit_config()
    except Exception:
        config = {}

    cats_from_db = _get_db_categories()
    merged_categories = {**config.get("categories", {}), **cats_from_db}

    return {
        "config": config,
        "categories": merged_categories,
        "texts": config.get("texts", {}),
        "style": config.get("style", {}),
        "color_scheme": config.get("style", {}).get("color_scheme", "dark"),
        "enabled": config.get("enabled", False),
    }


# ──────────────────────────────────────────────────────────────────────────────
#  {% cookiekit_script "category" %}…{% endcookiekit_script %}
# ──────────────────────────────────────────────────────────────────────────────

class CookieScriptNode(template.Node):
    """
    Rend le script encapsulé dans un bloc conditionnel JS.
    Le script n'est activé que si la catégorie est consentie.
    """

    def __init__(self, category: str, nodelist: template.NodeList) -> None:
        self.category = category
        self.nodelist = nodelist

    def render(self, context: template.Context) -> str:
        category = self.category.strip('"\'')
        inner = self.nodelist.render(context)
        # On encapsule le contenu dans un data-script pour activation JS lazy
        return (
            f'<script type="text/plain" data-xck-category="{category}" '
            f'data-xck-script="1">\n{inner}\n</script>'
        )


@register.tag("cookiekit_script")
def cookiekit_script_tag(parser: template.base.Parser, token: template.base.Token) -> CookieScriptNode:
    """
    Tag de bloc conditionnel :

    {% cookiekit_script "analytics" %}
      <script>...</script>
    {% endcookiekit_script %}
    """
    try:
        tag_name, category = token.split_contents()
    except ValueError as exc:
        raise template.TemplateSyntaxError(
            f"'{token.contents.split()[0]}' requiert exactement un argument (la catégorie)."
        ) from exc

    nodelist = parser.parse(("endcookiekit_script",))
    parser.delete_first_token()
    return CookieScriptNode(category, nodelist)


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers privés
# ──────────────────────────────────────────────────────────────────────────────

def _get_db_categories() -> dict:
    """Récupère les catégories depuis le modèle CookieCategory (si disponible)."""
    try:
        from xeolux_cookiekit.models import CookieCategory  # noqa: PLC0415

        result = {}
        for cat in CookieCategory.objects.all():
            result[cat.key] = {
                "label": cat.label,
                "description": cat.description,
                "required": cat.required,
                "enabled": cat.enabled,
            }
        return result
    except Exception:
        return {}


def _get_custom_scripts_html(position: str) -> str:
    """Récupère les CookieScript actifs pour une position (head/body)."""
    try:
        from xeolux_cookiekit.models import CookieScript  # noqa: PLC0415

        scripts = CookieScript.objects.filter(enabled=True, position=position)
        parts = []
        for script in scripts:
            parts.append(
                f'<script type="text/plain" data-xck-category="{script.category}" '
                f'data-xck-script="1">\n{script.script}\n</script>'
            )
        return "\n".join(parts)
    except Exception:
        return ""


def _build_integrations_js(integrations: dict) -> str:
    """
    Génère les blocs de scripts d'intégration depuis le dictionnaire de config.
    Délègue à integrations.build_integration_js() pour chaque intégration activée.
    """
    from xeolux_cookiekit.integrations import build_integration_js  # noqa: PLC0415

    parts = []
    for slug, cfg in integrations.items():
        if not cfg.get("enabled"):
            continue
        category = cfg.get("category", "analytics")
        js = build_integration_js(slug, cfg, category)
        if js:
            parts.append(js)
    return "\n".join(parts)
