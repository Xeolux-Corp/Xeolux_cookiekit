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

    lines = [
        ":root {",
        f"  --xck-bg: {_safe_color(style.get('background_color', '#111111'))};",
        f"  --xck-text: {_safe_color(style.get('text_color', '#ffffff'))};",
        f"  --xck-primary: {_safe_color(style.get('primary_color', '#ff6b00'))};",
        f"  --xck-primary-text: {_safe_color(style.get('primary_text_color', '#ffffff'))};",
        f"  --xck-secondary: {_safe_color(style.get('secondary_color', '#2b2b2b'))};",
        f"  --xck-secondary-text: {_safe_color(style.get('secondary_text_color', '#ffffff'))};",
        f"  --xck-radius: {radius};",
        f"  --xck-z-index: {z_index};",
        f"  --xck-shadow: {shadow_val};",
        f"  --xck-font: {_font_family(style.get('font_family', 'system'))};",
        "}",
    ]
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

    # GTM noscript
    gtm = integrations.get("google_tag_manager", {})
    if gtm.get("enabled") and gtm.get("container_id"):
        container_id = gtm["container_id"]
        # Validation du container ID
        if re.match(r'^GTM-[A-Z0-9]+$', container_id):
            parts.append(
                f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={container_id}" '
                f'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
            )

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
    Génère les blocs de scripts d'intégration encapsulés pour activation
    JS conditionnelle après consentement.
    """
    parts = []

    # ── Google Analytics ──────────────────────────────────────────────────
    ga = integrations.get("google_analytics", {})
    if ga.get("enabled") and ga.get("measurement_id"):
        mid = ga["measurement_id"]
        if re.match(r'^G-[A-Z0-9]+$', mid):
            category = ga.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'(function(){{\n'
                f'  var s=document.createElement("script");\n'
                f'  s.async=true;\n'
                f'  s.src="https://www.googletagmanager.com/gtag/js?id={mid}";\n'
                f'  document.head.appendChild(s);\n'
                f'  window.dataLayer=window.dataLayer||[];\n'
                f'  function gtag(){{dataLayer.push(arguments);}}\n'
                f'  window.gtag=gtag;\n'
                f'  gtag("js",new Date());\n'
                f'  gtag("config","{mid}");\n'
                f'}})();\n'
                f'</script>'
            )

    # ── Google Tag Manager ────────────────────────────────────────────────
    gtm = integrations.get("google_tag_manager", {})
    if gtm.get("enabled") and gtm.get("container_id"):
        cid = gtm["container_id"]
        if re.match(r'^GTM-[A-Z0-9]+$', cid):
            category = gtm.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{"gtm.start":\n'
                f'new Date().getTime(),event:"gtm.js"}});var f=d.getElementsByTagName(s)[0],\n'
                f'j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";j.async=true;j.src=\n'
                f'"https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);\n'
                f'}})(window,document,"script","dataLayer","{cid}");\n'
                f'</script>'
            )

    # ── Meta Pixel ────────────────────────────────────────────────────────
    meta = integrations.get("meta_pixel", {})
    if meta.get("enabled") and meta.get("pixel_id"):
        pid = meta["pixel_id"]
        if re.match(r'^\d+$', str(pid)):
            category = meta.get("category", "marketing")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{'
                f'n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};\n'
                f'if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";\n'
                f'n.queue=[];t=b.createElement(e);t.async=!0;\n'
                f't.src=v;s=b.getElementsByTagName(e)[0];\n'
                f's.parentNode.insertBefore(t,s)}}(window,document,"script",\n'
                f'"https://connect.facebook.net/en_US/fbevents.js");\n'
                f'fbq("init","{pid}");\n'
                f'fbq("track","PageView");\n'
                f'</script>'
            )

    # ── Matomo ────────────────────────────────────────────────────────────
    matomo = integrations.get("matomo", {})
    if matomo.get("enabled") and matomo.get("site_id") and matomo.get("tracker_url"):
        site_id = matomo["site_id"]
        tracker_url = matomo["tracker_url"].rstrip("/") + "/"
        # Validation basique
        if re.match(r'^\d+$', str(site_id)) and tracker_url.startswith("https://"):
            category = matomo.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'var _paq=window._paq=window._paq||[];\n'
                f'_paq.push(["trackPageView"]);\n'
                f'_paq.push(["enableLinkTracking"]);\n'
                f'(function(){{\n'
                f'  var u="{tracker_url}";\n'
                f'  _paq.push(["setTrackerUrl",u+"matomo.php"]);\n'
                f'  _paq.push(["setSiteId","{site_id}"]);\n'
                f'  var d=document,g=d.createElement("script"),s=d.getElementsByTagName("script")[0];\n'
                f'  g.async=true;g.src=u+"matomo.js";s.parentNode.insertBefore(g,s);\n'
                f'}})();\n'
                f'</script>'
            )

    # ── Plausible ─────────────────────────────────────────────────────────
    plausible = integrations.get("plausible", {})
    if plausible.get("enabled") and plausible.get("domain"):
        domain = plausible["domain"]
        script_url = plausible.get("script_url", "https://plausible.io/js/script.js")
        # Validation basique du domaine
        if re.match(r'^[a-zA-Z0-9._-]+$', domain) and script_url.startswith("https://"):
            category = plausible.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'(function(){{\n'
                f'  var s=document.createElement("script");\n'
                f'  s.defer=true;\n'
                f'  s.setAttribute("data-domain","{domain}");\n'
                f'  s.src="{script_url}";\n'
                f'  document.head.appendChild(s);\n'
                f'}})();\n'
                f'</script>'
            )

    # ── LinkedIn Insight Tag ───────────────────────────────────────────────
    linkedin = integrations.get("linkedin_insight", {})
    if linkedin.get("enabled") and linkedin.get("partner_id"):
        partner_id = str(linkedin["partner_id"])
        if re.match(r'^\d+$', partner_id):
            category = linkedin.get("category", "marketing")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'_linkedin_partner_id="{partner_id}";\n'
                f'window._linkedin_data_partner_ids=window._linkedin_data_partner_ids||[];\n'
                f'window._linkedin_data_partner_ids.push(_linkedin_partner_id);\n'
                f'(function(l){{\n'
                f'  if(!l){{window.lintrk=function(a,b){{window.lintrk.q.push([a,b])}};\n'
                f'  window.lintrk.q=[]}}\n'
                f'  var s=document.getElementsByTagName("script")[0];\n'
                f'  var b=document.createElement("script");\n'
                f'  b.type="text/javascript";b.async=true;\n'
                f'  b.src="https://snap.licdn.com/li.lms-analytics/insight.min.js";\n'
                f'  s.parentNode.insertBefore(b,s);\n'
                f'}})(window.lintrk);\n'
                f'</script>'
            )

    # ── TikTok Pixel ──────────────────────────────────────────────────────
    tiktok = integrations.get("tiktok_pixel", {})
    if tiktok.get("enabled") and tiktok.get("pixel_id"):
        pixel_id = tiktok["pixel_id"]
        if re.match(r'^[A-Z0-9]+$', pixel_id):
            category = tiktok.get("category", "marketing")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'!function(w,d,t){{\n'
                f'  w.TiktokAnalyticsObject=t;\n'
                f'  var ttq=w[t]=w[t]||[];\n'
                f'  ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];\n'
                f'  ttq.setAndDefer=function(t,e){{t[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};}};\n'
                f'  for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);\n'
                f'  ttq.instance=function(t){{for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e;}};\n'
                f'  ttq.load=function(e,n){{var i="https://analytics.tiktok.com/i18n/pixel/events.js";\n'
                f'  ttq._i=ttq._i||{{}};ttq._i[e]=[];ttq._i[e]._u=i;ttq._t=ttq._t||{{}};ttq._t[e]=+new Date;\n'
                f'  ttq._o=ttq._o||{{}};ttq._o[e]=n||{{}};\n'
                f'  var s=document.createElement("script");s.type="text/javascript";s.async=true;s.src=i+"?sdkid="+e+"&lib="+t;\n'
                f'  var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(s,a);\n'
                f'  }};\n'
                f'  ttq.load("{pixel_id}");\n'
                f'  ttq.page();\n'
                f'}}(window,document,"ttq");\n'
                f'</script>'
            )

    # ── Twitter / X Pixel ─────────────────────────────────────────────────
    twitter = integrations.get("twitter_pixel", {})
    if twitter.get("enabled") and twitter.get("pixel_id"):
        pixel_id = twitter["pixel_id"]
        if re.match(r'^[a-zA-Z0-9]+$', pixel_id):
            category = twitter.get("category", "marketing")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'!function(e,t,n,s,u,a){{\n'
                f'  e.twq||(s=e.twq=function(){{s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);}};\n'
                f'  s.version="1.1";s.queue=[];u=t.createElement(n);u.async=!0;\n'
                f'  u.src="https://static.ads-twitter.com/uwt.js";\n'
                f'  a=t.getElementsByTagName(n)[0];a.parentNode.insertBefore(u,a);\n'
                f'}}(window,document,"script");\n'
                f'twq("config","{pixel_id}");\n'
                f'</script>'
            )

    # ── Microsoft Clarity ─────────────────────────────────────────────────
    clarity = integrations.get("clarity", {})
    if clarity.get("enabled") and clarity.get("project_id"):
        project_id = clarity["project_id"]
        if re.match(r'^[a-z0-9]+$', project_id):
            category = clarity.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'(function(c,l,a,r,i,t,y){{\n'
                f'  c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};\n'
                f'  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;\n'
                f'  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);\n'
                f'}})(window,document,"clarity","script","{project_id}");\n'
                f'</script>'
            )

    # ── Hotjar ────────────────────────────────────────────────────────────
    hotjar = integrations.get("hotjar", {})
    if hotjar.get("enabled") and hotjar.get("site_id"):
        site_id = str(hotjar["site_id"])
        if re.match(r'^\d+$', site_id):
            category = hotjar.get("category", "analytics")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'(function(h,o,t,j,a,r){{\n'
                f'  h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};\n'
                f'  h._hjSettings={{hjid:{site_id},hjsv:6}};\n'
                f'  a=o.getElementsByTagName("head")[0];\n'
                f'  r=o.createElement("script");r.async=1;\n'
                f'  r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;\n'
                f'  a.appendChild(r);\n'
                f'}})(window,document,"https://static.hotjar.com/c/hotjar-",".js?sv=");\n'
                f'</script>'
            )

    # ── Crisp Chat ────────────────────────────────────────────────────────
    crisp = integrations.get("crisp", {})
    if crisp.get("enabled") and crisp.get("website_id"):
        website_id = crisp["website_id"]
        # UUID format validation
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', website_id.lower()):
            category = crisp.get("category", "preferences")
            parts.append(
                f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
                f'window.$crisp=[];window.CRISP_WEBSITE_ID="{website_id}";\n'
                f'(function(){{\n'
                f'  var d=document;var s=d.createElement("script");\n'
                f'  s.src="https://client.crisp.chat/l.js";s.async=1;\n'
                f'  d.getElementsByTagName("head")[0].appendChild(s);\n'
                f'}})();\n'
                f'</script>'
            )

    return "\n".join(parts)
