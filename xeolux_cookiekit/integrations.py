"""
integrations.py — Catalogue des intégrations tierces et générateur JS.

Chaque intégration est définie par :
  - label     : Nom affiché dans l'admin
  - category  : Catégorie de consentement (analytics / marketing / preferences / support)
  - order     : Ordre d'affichage dans l'admin
  - fields    : Champs de configuration attendus dans le JSONField
  - build_js  : Fonction qui génère le bloc <script> à injecter (conditionné au consentement JS)

Ajouter une intégration = ajouter une entrée dans INTEGRATION_CATALOG.
Aucune migration DB nécessaire — les intégrations inconnues sont auto-créées via post_migrate.
"""

from __future__ import annotations

import re

# ──────────────────────────────────────────────────────────────────────────────
#  Catalogue des intégrations
# ──────────────────────────────────────────────────────────────────────────────

INTEGRATION_CATALOG: dict[str, dict] = {

    # ── Analytics ─────────────────────────────────────────────────────────────

    "google_analytics": {
        "label": "Google Analytics 4",
        "category": "analytics",
        "order": 10,
        "fields": {
            "measurement_id": {
                "label": "Measurement ID",
                "help": "Exemple : G-XXXXXXXXXX",
                "placeholder": "G-XXXXXXXXXX",
            }
        },
    },

    "google_tag_manager": {
        "label": "Google Tag Manager",
        "category": "analytics",
        "order": 11,
        "fields": {
            "container_id": {
                "label": "Container ID",
                "help": "Exemple : GTM-XXXXXXX",
                "placeholder": "GTM-XXXXXXX",
            }
        },
    },

    "matomo": {
        "label": "Matomo",
        "category": "analytics",
        "order": 20,
        "fields": {
            "site_id": {"label": "Site ID", "help": "Exemple : 1"},
            "tracker_url": {
                "label": "Tracker URL",
                "help": "Exemple : https://matomo.example.com/",
                "placeholder": "https://matomo.example.com/",
            },
        },
    },

    "plausible": {
        "label": "Plausible Analytics",
        "category": "analytics",
        "order": 21,
        "fields": {
            "domain": {"label": "Domaine", "help": "Exemple : monsite.com"},
            "script_url": {
                "label": "URL du script (optionnel)",
                "help": "Par défaut : https://plausible.io/js/script.js",
                "placeholder": "https://plausible.io/js/script.js",
            },
        },
    },

    "clarity": {
        "label": "Microsoft Clarity",
        "category": "analytics",
        "order": 22,
        "fields": {
            "project_id": {
                "label": "Project ID",
                "help": "Exemple : abcde12345 (Settings → Clarity)",
            }
        },
    },

    "hotjar": {
        "label": "Hotjar",
        "category": "analytics",
        "order": 23,
        "fields": {
            "site_id": {"label": "Site ID", "help": "Exemple : 1234567"}
        },
    },

    "mixpanel": {
        "label": "Mixpanel",
        "category": "analytics",
        "order": 24,
        "fields": {
            "project_token": {
                "label": "Project Token",
                "help": "Trouvé dans Settings → Project Details",
            }
        },
    },

    "amplitude": {
        "label": "Amplitude",
        "category": "analytics",
        "order": 25,
        "fields": {
            "api_key": {
                "label": "API Key",
                "help": "Trouvé dans Settings → Projects",
            }
        },
    },

    "posthog": {
        "label": "PostHog",
        "category": "analytics",
        "order": 26,
        "fields": {
            "api_key": {
                "label": "API Key",
                "help": "Exemple : phc_XXXXXXXXXXXXXXXXXXXX",
            },
            "host": {
                "label": "Host (optionnel)",
                "help": "Par défaut : https://app.posthog.com",
                "placeholder": "https://app.posthog.com",
            },
        },
    },

    "umami": {
        "label": "Umami Analytics",
        "category": "analytics",
        "order": 27,
        "fields": {
            "website_id": {
                "label": "Website ID",
                "help": "UUID du site dans votre instance Umami",
            },
            "script_url": {
                "label": "URL du script",
                "help": "Exemple : https://analytics.monsite.com/script.js",
            },
        },
    },

    "fathom": {
        "label": "Fathom Analytics",
        "category": "analytics",
        "order": 28,
        "fields": {
            "site_id": {
                "label": "Site ID",
                "help": "Exemple : ABCDE (4-5 caractères majuscules)",
            }
        },
    },

    "segment": {
        "label": "Segment",
        "category": "analytics",
        "order": 29,
        "fields": {
            "write_key": {
                "label": "Write Key",
                "help": "Trouvé dans Settings → API Keys de votre source",
            }
        },
    },

    "heap": {
        "label": "Heap Analytics",
        "category": "analytics",
        "order": 30,
        "fields": {
            "app_id": {
                "label": "App ID",
                "help": "Exemple : 1234567890 (dans Account → App ID)",
            }
        },
    },

    "fullstory": {
        "label": "FullStory",
        "category": "analytics",
        "order": 31,
        "fields": {
            "org_id": {
                "label": "Org ID",
                "help": "Trouvé dans Settings → General → Org ID",
            }
        },
    },

    "cloudflare_web_analytics": {
        "label": "Cloudflare Web Analytics",
        "category": "analytics",
        "order": 32,
        "fields": {
            "token": {
                "label": "Beacon Token",
                "help": "Token généré dans Cloudflare → Web Analytics → Manage Site",
            }
        },
    },

    # ── Marketing ─────────────────────────────────────────────────────────────

    "meta_pixel": {
        "label": "Meta Pixel (Facebook)",
        "category": "marketing",
        "order": 40,
        "fields": {
            "pixel_id": {
                "label": "Pixel ID",
                "help": "Exemple : 1234567890123456",
            }
        },
    },

    "linkedin_insight": {
        "label": "LinkedIn Insight Tag",
        "category": "marketing",
        "order": 41,
        "fields": {
            "partner_id": {
                "label": "Partner ID",
                "help": "Exemple : 1234567",
            }
        },
    },

    "tiktok_pixel": {
        "label": "TikTok Pixel",
        "category": "marketing",
        "order": 42,
        "fields": {
            "pixel_id": {
                "label": "Pixel ID",
                "help": "Exemple : C3XXXXXXXXXXXXXXXX",
            }
        },
    },

    "twitter_pixel": {
        "label": "Twitter / X Universal Website Tag",
        "category": "marketing",
        "order": 43,
        "fields": {
            "pixel_id": {
                "label": "Pixel ID",
                "help": "Exemple : o2345",
            }
        },
    },

    "pinterest_tag": {
        "label": "Pinterest Tag",
        "category": "marketing",
        "order": 44,
        "fields": {
            "tag_id": {
                "label": "Tag ID",
                "help": "Exemple : 2619525912345",
            }
        },
    },

    "snapchat_pixel": {
        "label": "Snapchat Pixel",
        "category": "marketing",
        "order": 45,
        "fields": {
            "pixel_id": {
                "label": "Pixel ID",
                "help": "UUID trouvé dans Snap Ads Manager → Snap Pixel",
            }
        },
    },

    "reddit_pixel": {
        "label": "Reddit Pixel",
        "category": "marketing",
        "order": 46,
        "fields": {
            "advertiser_id": {
                "label": "Advertiser ID",
                "help": "Exemple : t2_XXXXXXXX",
            }
        },
    },

    "quora_pixel": {
        "label": "Quora Pixel",
        "category": "marketing",
        "order": 47,
        "fields": {
            "pixel_id": {
                "label": "Pixel ID",
                "help": "Exemple : abc123def456 (Quora Ads → Quora Pixel)",
            }
        },
    },

    # ── Support / Chat ─────────────────────────────────────────────────────────

    "crisp": {
        "label": "Crisp Chat",
        "category": "preferences",
        "order": 60,
        "fields": {
            "website_id": {
                "label": "Website ID",
                "help": "UUID : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            }
        },
    },

    "intercom": {
        "label": "Intercom",
        "category": "preferences",
        "order": 61,
        "fields": {
            "app_id": {
                "label": "App ID",
                "help": "Exemple : abc12def (Settings → Installation)",
            }
        },
    },

    "hubspot": {
        "label": "HubSpot Tracking",
        "category": "analytics",
        "order": 62,
        "fields": {
            "portal_id": {
                "label": "Portal ID (Hub ID)",
                "help": "Exemple : 1234567 (visible dans l'URL HubSpot)",
            }
        },
    },

    "zendesk": {
        "label": "Zendesk Chat (Web Widget)",
        "category": "preferences",
        "order": 63,
        "fields": {
            "key": {
                "label": "Widget Key",
                "help": "Clé UUID du widget dans Settings → Channels → Widget",
            }
        },
    },

    "tidio": {
        "label": "Tidio Chat",
        "category": "preferences",
        "order": 64,
        "fields": {
            "public_key": {
                "label": "Public Key",
                "help": "Exemple : abcdef1234567890abcdef1234567890",
            }
        },
    },

    "brevo": {
        "label": "Brevo (ex-Sendinblue) Tracker",
        "category": "marketing",
        "order": 65,
        "fields": {
            "client_key": {
                "label": "Client Key",
                "help": "Trouvé dans Brevo → Transactional → Settings → Tracking code",
            }
        },
    },

    "freshchat": {
        "label": "Freshchat",
        "category": "preferences",
        "order": 66,
        "fields": {
            "token": {
                "label": "Token",
                "help": "Trouvé dans Admin → Account Setup → Web Messenger",
            },
            "host": {
                "label": "Host (optionnel)",
                "help": "Par défaut : https://wchat.freshchat.com",
            },
        },
    },
}


# ──────────────────────────────────────────────────────────────────────────────
#  Générateurs JS — un par intégration
#  Chaque fonction retourne un bloc <script type="text/plain" data-xck-*>
# ──────────────────────────────────────────────────────────────────────────────

def _wrap(category: str, code: str) -> str:
    """Encapsule le code dans un bloc conditionnel CookieKit."""
    return (
        f'<script type="text/plain" data-xck-category="{category}" data-xck-script="1">\n'
        f'{code}\n'
        f'</script>'
    )


def build_google_analytics(cfg: dict, category: str) -> str:
    mid = cfg.get("measurement_id", "")
    if not re.match(r'^G-[A-Z0-9]+$', mid):
        return ""
    return _wrap(category, (
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
        f'}})();'
    ))


def build_google_tag_manager(cfg: dict, category: str) -> str:
    cid = cfg.get("container_id", "")
    if not re.match(r'^GTM-[A-Z0-9]+$', cid):
        return ""
    return _wrap(category, (
        f'(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{"gtm.start":\n'
        f'new Date().getTime(),event:"gtm.js"}});var f=d.getElementsByTagName(s)[0],\n'
        f'j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";j.async=true;j.src=\n'
        f'"https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);\n'
        f'}})(window,document,"script","dataLayer","{cid}");'
    ))


def build_matomo(cfg: dict, category: str) -> str:
    site_id = str(cfg.get("site_id", ""))
    tracker_url = cfg.get("tracker_url", "").rstrip("/") + "/"
    if not re.match(r'^\d+$', site_id):
        return ""
    if not tracker_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'var _paq=window._paq=window._paq||[];\n'
        f'_paq.push(["trackPageView"]);\n'
        f'_paq.push(["enableLinkTracking"]);\n'
        f'(function(){{\n'
        f'  var u="{tracker_url}";\n'
        f'  _paq.push(["setTrackerUrl",u+"matomo.php"]);\n'
        f'  _paq.push(["setSiteId","{site_id}"]);\n'
        f'  var d=document,g=d.createElement("script"),s=d.getElementsByTagName("script")[0];\n'
        f'  g.async=true;g.src=u+"matomo.js";s.parentNode.insertBefore(g,s);\n'
        f'}})();'
    ))


def build_plausible(cfg: dict, category: str) -> str:
    domain = cfg.get("domain", "")
    script_url = cfg.get("script_url", "https://plausible.io/js/script.js") or "https://plausible.io/js/script.js"
    if not re.match(r'^[a-zA-Z0-9._-]+$', domain):
        return ""
    if not script_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.defer=true;\n'
        f'  s.setAttribute("data-domain","{domain}");\n'
        f'  s.src="{script_url}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_clarity(cfg: dict, category: str) -> str:
    pid = cfg.get("project_id", "")
    if not re.match(r'^[a-z0-9]+$', pid):
        return ""
    return _wrap(category, (
        f'(function(c,l,a,r,i,t,y){{\n'
        f'  c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};\n'
        f'  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;\n'
        f'  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);\n'
        f'}})(window,document,"clarity","script","{pid}");'
    ))


def build_hotjar(cfg: dict, category: str) -> str:
    site_id = str(cfg.get("site_id", ""))
    if not re.match(r'^\d+$', site_id):
        return ""
    return _wrap(category, (
        f'(function(h,o,t,j,a,r){{\n'
        f'  h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};\n'
        f'  h._hjSettings={{hjid:{site_id},hjsv:6}};\n'
        f'  a=o.getElementsByTagName("head")[0];\n'
        f'  r=o.createElement("script");r.async=1;\n'
        f'  r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;\n'
        f'  a.appendChild(r);\n'
        f'}})(window,document,"https://static.hotjar.com/c/hotjar-",".js?sv=");'
    ))


def build_mixpanel(cfg: dict, category: str) -> str:
    token = cfg.get("project_token", "")
    if not re.match(r'^[a-zA-Z0-9]+$', token):
        return ""
    return _wrap(category, (
        f'(function(f,b){{if(!b.__SV){{var e,g,i,h;window.mixpanel=b;b._i=[];'
        f'b.init=function(e,f,c){{function g(a,d){{var b=d.split(".");2==b.length&&(a=a[b[0]],d=b[1]);'
        f'a[d]=function(){{a.push([d].concat(Array.prototype.slice.call(arguments,0)))}};}}'
        f'var a=b;"undefined"!==typeof c?a=b[c]=[]:c="mixpanel";'
        f'a.people=a.people||[];a.toString=function(a){{var d="mixpanel";"mixpanel"!==c&&(d+="."+c);'
        f'a||(d+=" (stub)");return d}};a.people.toString=function(){{return a.toString(1)+".people (stub)";}};'
        f'i="disable time_event track track_pageview track_links track_forms track_with_groups add_group set_group remove_group register register_once alias unregister identify name_tag set_config reset opt_in_tracking opt_out_tracking has_opted_in_tracking has_opted_out_tracking clear_opt_in_out_tracking start_batch_senders people.set people.set_once people.unset people.increment people.append people.union people.track_charge people.clear_charges people.delete_user people.remove".split(" ");'
        f'for(h=0;h<i.length;h++)g(a,i[h]);var j="set set_once union unset remove delete".split(" ");'
        f'a.get_group=function(){{for(var b=new Array(arguments.length-1),c=1;c<arguments.length;c++)b[c-1]=arguments[c];'
        f'return{{fn:function(c){{b.unshift(c);a.push([e].concat(b))}}}}}};'
        f'b._i.push([e,f,c])}};b.__SV=1.2;e=f.createElement("script");'
        f'e.type="text/javascript";e.async=!0;e.src="https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js";'
        f'g=f.getElementsByTagName("script")[0];g.parentNode.insertBefore(e,g);}}}}'
        f')(document,window.mixpanel||[]);\n'
        f'mixpanel.init("{token}",{{track_pageview:true}});'
    ))


def build_amplitude(cfg: dict, category: str) -> str:
    api_key = cfg.get("api_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', api_key):
        return ""
    return _wrap(category, (
        f'(function(e,t){{var n=e.amplitude||{{}};if(n.invoked){{e.console&&console.error&&console.error("Amplitude snippet has been loaded.");}}'
        f'else{{n.invoked=true;n._q=[];var s=["add","append","clearAll","prepend","set","setOnce","unset","preInsert","postInsert","remove","getUserProperties"];'
        f'n.Identify=function(){{}};for(var i=0;i<s.length;i++){{(function(t){{n.Identify.prototype[t]=function(){{this._q.push([t].concat(Array.prototype.slice.call(arguments,0)));return this;}}}})(s[i]);}} '
        f'n.Revenue=function(){{}};var r=["setProductId","setQuantity","setPrice","setRevenueType","setEventProperties"];'
        f'for(var i=0;i<r.length;i++){{(function(t){{n.Revenue.prototype[t]=function(){{this._q.push([t].concat(Array.prototype.slice.call(arguments,0)));return this;}}}})(r[i]);}}'
        f'var a=["init","logEvent","logRevenue","setUserId","setUserProperties","setOptOut","setVersionName","setDomain","setDeviceId","enableTracking","setGlobalUserProperties","identify","clearUserProperties","setGroup","logRevenueV2","regenerateDeviceId","groupIdentify","onInit","logEventWithTimestamp","logGroup","setSessionId","resetSessionId","getDeviceId","getUserId","setMinTimeBetweenSessionsMillis","setEventUploadThreshold","setUseDynamicConfig","setServerZone","setServerUrl","sendEvents","setLibrary","setTransport"];'
        f'for(var i=0;i<a.length;i++){{(function(t){{n[t]=function(){{n._q.push([t].concat(Array.prototype.slice.call(arguments,0)));}}}})(a[i]);}}'
        f'n.init=function(e,t,i){{n._q.unshift(["init",e,t,i]);}};e.amplitude=n;'
        f'var c=t.createElement("script");c.type="text/javascript";c.async=true;c.src="https://cdn.amplitude.com/libs/amplitude-8.21.4-min.gz.js";'
        f'var d=t.getElementsByTagName("script")[0];d.parentNode.insertBefore(c,d);}}}}'
        f')(window,document);\n'
        f'amplitude.getInstance().init("{api_key}");'
    ))


def build_posthog(cfg: dict, category: str) -> str:
    api_key = cfg.get("api_key", "")
    host = cfg.get("host", "https://app.posthog.com") or "https://app.posthog.com"
    if not re.match(r'^phc_[a-zA-Z0-9]+$', api_key):
        return ""
    if not host.startswith("https://"):
        return ""
    return _wrap(category, (
        f'!function(t,e){{var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){{'
        f'function g(t,e){{var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]);'
        f't[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}}'
        f'(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,'
        f'p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);'
        f'var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){{'
        f'var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}},u.people.toString=function(){{'
        f'return u.toString(1)+".people (stub)"}},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys".split(" "),n=0;'
        f'n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])}},e.__SV=1)}}'
        f'(document,window.posthog||[]);\n'
        f'posthog.init("{api_key}",{{api_host:"{host}"}});'
    ))


def build_umami(cfg: dict, category: str) -> str:
    website_id = cfg.get("website_id", "")
    script_url = cfg.get("script_url", "")
    if not re.match(r'^[0-9a-f-]+$', website_id.lower()):
        return ""
    if not script_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.defer=true;\n'
        f'  s.setAttribute("data-website-id","{website_id}");\n'
        f'  s.src="{script_url}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_fathom(cfg: dict, category: str) -> str:
    site_id = cfg.get("site_id", "")
    if not re.match(r'^[A-Z]{4,8}$', site_id):
        return ""
    return _wrap(category, (
        f'(function(f,a,t,h,o,m){{\n'
        f'  a[h]=a[h]||function(){{\n'
        f'    (a[h].q=a[h].q||[]).push(arguments)\n'
        f'  }};\n'
        f'  o=f.createElement("script"),m=f.getElementsByTagName("script")[0];\n'
        f'  o.async=1;o.src="https://cdn.usefathom.com/script.js";\n'
        f'  o.setAttribute("data-site","{site_id}");\n'
        f'  m.parentNode.insertBefore(o,m);\n'
        f'}})(document,window,"script","fathom");'
    ))


def build_segment(cfg: dict, category: str) -> str:
    write_key = cfg.get("write_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', write_key):
        return ""
    return _wrap(category, (
        f'!function(){{var i="analytics",analytics=window[i]=window[i]||[];'
        f'if(!analytics.initialize)if(analytics.invoked)window.console&&console.error&&console.error("Segment snippet included twice.");'
        f'else{{analytics.invoked=!0;analytics.methods=["trackSubmit","trackClick","trackLink","trackForm","pageview","identify","reset","group","track","ready","alias","debug","page","screen","once","off","on","addSourceMiddleware","addIntegrationMiddleware","setAnonymousId","addDestinationMiddleware","register"];'
        f'analytics.factory=function(e){{return function(){{if(window[i].initialized)return window[i][e].apply(window[i],arguments);var n=Array.prototype.slice.call(arguments);'
        f'if(["track","screen","alias","group","page","identify"].indexOf(e)>-1){{var c=document.querySelector("link[rel=\'canonical\']");n.push({{__t:"bpc",c:c&&c.getAttribute("href")||void 0,p:document.path||void 0,u:document.URL||void 0,s:document.referrer||void 0,t:document.title||void 0,o:document.domain||void 0}});}}'
        f'n.unshift(e);analytics.push(n);return analytics}}}};'
        f'for(var n=0;n<analytics.methods.length;n++){{var key=analytics.methods[n];analytics[key]=analytics.factory(key);}}'
        f'analytics.load=function(key,n){{var t=document.createElement("script");t.type="text/javascript";t.async=!0;'
        f't.src="https://cdn.segment.com/analytics.js/v1/"+key+"/analytics.min.js";'
        f'var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(t,r);analytics._loadOptions=n;}};'
        f'analytics._writeKey="{write_key}";analytics.SNIPPET_VERSION="5.2.1";analytics.load("{write_key}");analytics.page();}}}}'
        f'();'
    ))


def build_heap(cfg: dict, category: str) -> str:
    app_id = str(cfg.get("app_id", ""))
    if not re.match(r'^\d+$', app_id):
        return ""
    return _wrap(category, (
        f'window.heap=window.heap||[],heap.config={{}};'
        f'heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};'
        f'var r=document.createElement("script");r.type="text/javascript",r.async=!0,'
        f'r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";'
        f'var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);'
        f'for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)'
        f'heap[p[o]]=n(p[o])}};\n'
        f'heap.load("{app_id}");'
    ))


def build_fullstory(cfg: dict, category: str) -> str:
    org_id = cfg.get("org_id", "")
    if not re.match(r'^[A-Z0-9]+$', org_id):
        return ""
    return _wrap(category, (
        f'window["_fs_debug"]=false;window["_fs_host"]="fullstory.com";'
        f'window["_fs_script"]="edge.fullstory.com/s/fs.js";window["_fs_org"]="{org_id}";'
        f'window["_fs_namespace"]="FS";'
        f'(function(m,n,e,t,l,o,g,y){{\n'
        f'  if(e in m){{if(m.console&&m.console.log)m.console.log("FullStory namespace conflict. Please set window[\'_fs_namespace\'].");return;}}\n'
        f'  g=m[e]=function(a,b,s){{g.q?g.q.push([a,b,s]):g._api(a,b,s);}};g.q=[];'
        f'  o=n.createElement(t);o.async=1;o.crossOrigin="anonymous";o.src="https://"+_fs_script;'
        f'  y=n.getElementsByTagName(t)[0];y.parentNode.insertBefore(o,y);\n'
        f'  g.identify=function(i,v,s){{g(l,{{uid:i}},s);if(v)g(l,v,s)}};'
        f'  g.setUserVars=function(v,s){{g(l,v,s)}};g.event=function(i,v,s){{g("event",{{n:i,p:v}},s);}};'
        f'  g.anonymize=function(){{g.identify(!!0)}};'
        f'  g.shutdown=function(){{g("rec",!1)}};g.restart=function(){{g("rec",!0)}};'
        f'  g.log=function(a,b){{g("log",[a,b])}};'
        f'  g.consent=function(a){{g("consent",!arguments.length||a)}};'
        f'  g.identifyAccount=function(i,v){{o="account";v=v||{{}};v.acctId=i;g(o,v)}};'
        f'  g.clearUserCookie=function(){{}};'
        f'  g.setVars=function(n,p){{g("setVars",[n,p]);}};'
        f'  g._w={{}};y="XMLHttpRequest";g._w[y]=m[y];y="fetch";g._w[y]=m[y];'
        f'  if(m[y])m[y]=function(){{return g._w[y].apply(this,arguments)}};'
        f'  g._v="1.3.0";\n'
        f'}})(window,document,window["_fs_namespace"],"script","user");'
    ))


def build_cloudflare_web_analytics(cfg: dict, category: str) -> str:
    token = cfg.get("token", "")
    if not re.match(r'^[a-zA-Z0-9]+$', token):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.defer=true;\n'
        f'  s.src="https://static.cloudflareinsights.com/beacon.min.js";\n'
        f'  s.setAttribute("data-cf-beacon",\'{{"token":"{token}"}}\');\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_meta_pixel(cfg: dict, category: str) -> str:
    pid = str(cfg.get("pixel_id", ""))
    if not re.match(r'^\d+$', pid):
        return ""
    return _wrap(category, (
        f'!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{'
        f'n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};\n'
        f'if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";\n'
        f'n.queue=[];t=b.createElement(e);t.async=!0;\n'
        f't.src=v;s=b.getElementsByTagName(e)[0];\n'
        f's.parentNode.insertBefore(t,s)}}(window,document,"script",\n'
        f'"https://connect.facebook.net/en_US/fbevents.js");\n'
        f'fbq("init","{pid}");\n'
        f'fbq("track","PageView");'
    ))


def build_linkedin_insight(cfg: dict, category: str) -> str:
    pid = str(cfg.get("partner_id", ""))
    if not re.match(r'^\d+$', pid):
        return ""
    return _wrap(category, (
        f'_linkedin_partner_id="{pid}";\n'
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
        f'}})(window.lintrk);'
    ))


def build_tiktok_pixel(cfg: dict, category: str) -> str:
    pid = cfg.get("pixel_id", "")
    if not re.match(r'^[A-Z0-9]+$', pid):
        return ""
    return _wrap(category, (
        f'!function(w,d,t){{\n'
        f'  w.TiktokAnalyticsObject=t;\n'
        f'  var ttq=w[t]=w[t]||[];\n'
        f'  ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];\n'
        f'  ttq.setAndDefer=function(t,e){{t[e]=function(){{t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}};\n'
        f'  for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);\n'
        f'  ttq.load=function(e,n){{var i="https://analytics.tiktok.com/i18n/pixel/events.js";\n'
        f'  ttq._i=ttq._i||{{}};ttq._i[e]=[];ttq._i[e]._u=i;ttq._t=ttq._t||{{}};\n'
        f'  ttq._t[e]=+new Date;ttq._o=ttq._o||{{}};ttq._o[e]=n||{{}};\n'
        f'  var s=document.createElement("script");s.type="text/javascript";s.async=true;\n'
        f'  s.src=i+"?sdkid="+e+"&lib="+t;\n'
        f'  var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(s,a);\n'
        f'  }};\n'
        f'  ttq.load("{pid}");\n'
        f'  ttq.page();\n'
        f'}}(window,document,"ttq");'
    ))


def build_twitter_pixel(cfg: dict, category: str) -> str:
    pid = cfg.get("pixel_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', pid):
        return ""
    return _wrap(category, (
        f'!function(e,t,n,s,u,a){{\n'
        f'  e.twq||(s=e.twq=function(){{s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);}};\n'
        f'  s.version="1.1";s.queue=[];u=t.createElement(n);u.async=!0;\n'
        f'  u.src="https://static.ads-twitter.com/uwt.js";\n'
        f'  a=t.getElementsByTagName(n)[0];a.parentNode.insertBefore(u,a);\n'
        f'}}(window,document,"script");\n'
        f'twq("config","{pid}");'
    ))


def build_pinterest_tag(cfg: dict, category: str) -> str:
    tag_id = str(cfg.get("tag_id", ""))
    if not re.match(r'^\d+$', tag_id):
        return ""
    return _wrap(category, (
        f'!function(e){{if(!window.pintrk){{window.pintrk=function(){{window.pintrk.queue.push(Array.prototype.slice.call(arguments))}};\n'
        f'var n=window.pintrk;n.queue=[],n.version="3.0";\n'
        f'var t=document.createElement("script");t.async=!0,t.src=e;\n'
        f'var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(t,r)}}}}'
        f'("https://s.pinimg.com/ct/core.js");\n'
        f'pintrk("load","{tag_id}");\n'
        f'pintrk("page");'
    ))


def build_snapchat_pixel(cfg: dict, category: str) -> str:
    pid = cfg.get("pixel_id", "")
    if not re.match(r'^[0-9a-f-]+$', pid.lower()):
        return ""
    return _wrap(category, (
        f'(function(e,t,n){{if(e.snaptr)return;var a=e.snaptr=function(){{'
        f'a.handleRequest?a.handleRequest.apply(a,arguments):a.queue.push(arguments)}};\n'
        f'a.queue=[];var s="script";r=t.createElement(s);r.async=!0;\n'
        f'r.src=n;var u=t.getElementsByTagName(s)[0];\n'
        f'u.parentNode.insertBefore(r,u);}})(window,document,\n'
        f'"https://sc-static.net/scevent.min.js");\n'
        f'snaptr("init","{pid}");\n'
        f'snaptr("track","PAGE_VIEW");'
    ))


def build_reddit_pixel(cfg: dict, category: str) -> str:
    adv_id = cfg.get("advertiser_id", "")
    if not re.match(r'^t2_[a-zA-Z0-9]+$', adv_id):
        return ""
    return _wrap(category, (
        f'!function(w,d){{if(!w.rdt){{var p=w.rdt=function(){{p.sendEvent?p.sendEvent.apply(p,arguments):p.callQueue.push(arguments)}};'
        f'p.callQueue=[];var t=d.createElement("script");t.src="https://www.redditstatic.com/ads/v2.js",t.async=1;\n'
        f'var s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(t,s)}}}}'
        f'(window,document);\n'
        f'rdt("init","{adv_id}");\n'
        f'rdt("track","PageVisit");'
    ))


def build_quora_pixel(cfg: dict, category: str) -> str:
    pid = cfg.get("pixel_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', pid):
        return ""
    return _wrap(category, (
        f'!function(q,e,v,n,t,s){{if(q.qp)return;n=q.qp=function(){{n.qp?n.qp.apply(n,arguments):'
        f'n.queue.push(arguments)}};n.queue=[];t=document.createElement(e);t.async=!0;\n'
        f't.src=v;s=document.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s);}}'
        f'(window,"script","https://a.quora.com/qevents.js");\n'
        f'qp("init","{pid}");\n'
        f'qp("track","ViewContent");'
    ))


def build_crisp(cfg: dict, category: str) -> str:
    wid = cfg.get("website_id", "")
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', wid.lower()):
        return ""
    return _wrap(category, (
        f'window.$crisp=[];window.CRISP_WEBSITE_ID="{wid}";\n'
        f'(function(){{\n'
        f'  var d=document;var s=d.createElement("script");\n'
        f'  s.src="https://client.crisp.chat/l.js";s.async=1;\n'
        f'  d.getElementsByTagName("head")[0].appendChild(s);\n'
        f'}})();'
    ))


def build_intercom(cfg: dict, category: str) -> str:
    app_id = cfg.get("app_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', app_id):
        return ""
    return _wrap(category, (
        f'(function(){{var w=window;var ic=w.Intercom;\n'
        f'if(typeof ic==="function"){{ic("reattach_activator");ic("update",w.intercomSettings);}}'
        f'else{{var d=document;var i=function(){{i.c(arguments)}};i.q=[];i.c=function(args){{i.q.push(args);}};\n'
        f'w.Intercom=i;var l=function(){{var s=d.createElement("script");s.type="text/javascript";\n'
        f's.async=true;s.src="https://widget.intercom.io/widget/{app_id}";\n'
        f'var x=d.getElementsByTagName("script")[0];x.parentNode.insertBefore(s,x);}};\n'
        f'if(document.readyState==="complete"){{l();}}else if(w.attachEvent){{w.attachEvent("onload",l);}}'
        f'else{{w.addEventListener("load",l,false);}}}}}})()\n'
        f'Intercom("boot",{{app_id:"{app_id}"}});'
    ))


def build_hubspot(cfg: dict, category: str) -> str:
    portal_id = str(cfg.get("portal_id", ""))
    if not re.match(r'^\d+$', portal_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.type="text/javascript";\n'
        f'  s.id="hs-script-loader";\n'
        f'  s.async=true;s.defer=true;\n'
        f'  s.src="//js.hs-scripts.com/{portal_id}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_zendesk(cfg: dict, category: str) -> str:
    key = cfg.get("key", "")
    if not re.match(r'^[0-9a-f-]+$', key.lower()):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.id="ze-snippet";\n'
        f'  s.src="https://static.zdassets.com/ekr/snippet.js?key={key}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_tidio(cfg: dict, category: str) -> str:
    key = cfg.get("public_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', key):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.async=true;\n'
        f'  s.src="//code.tidio.co/{key}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_brevo(cfg: dict, category: str) -> str:
    client_key = cfg.get("client_key", "")
    if not re.match(r'^[a-zA-Z0-9-]+$', client_key):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  window.sib = {{equeue:[],client_key:"{client_key}"}};\n'
        f'  window.sendinblue = {{}};\n'
        f'  for(var j=["track","identify","trackLink","page"],i=0;i<j.length;i++){{(function(k){{\n'
        f'    window.sendinblue[k]=function(){{var args=Array.prototype.slice.call(arguments);\n'
        f'    (window.sib.equeue=window.sib.equeue||[]).push({{method:k,params:args}});}}\n'
        f'  }})(j[i]);}}\n'
        f'  var n=document.createElement("script");\n'
        f'  n.type="text/javascript";\n'
        f'  n.id="sendinblue-js";\n'
        f'  n.async=true;\n'
        f'  n.src="https://sibautomation.com/sa.js?key={client_key}";\n'
        f'  var s=document.getElementsByTagName("script")[0];\n'
        f'  s.parentNode.insertBefore(n,s);\n'
        f'  window.sendinblue.page();\n'
        f'}})();'
    ))


def build_freshchat(cfg: dict, category: str) -> str:
    token = cfg.get("token", "")
    host = cfg.get("host", "https://wchat.freshchat.com") or "https://wchat.freshchat.com"
    if not re.match(r'^[a-zA-Z0-9-]+$', token):
        return ""
    if not host.startswith("https://"):
        return ""
    return _wrap(category, (
        f'function initFreshChat(){{\n'
        f'  window.fcWidget.init({{\n'
        f'    token:"{token}",\n'
        f'    host:"{host}"\n'
        f'  }});\n'
        f'}}\n'
        f'function initialize(i,t){{\n'
        f'  var e;i.getElementById(t)?initFreshChat():\n'
        f'  ((e=i.createElement("script")).id=t,e.async=!0,\n'
        f'  e.src="https://wchat.freshchat.com/js/widget.js",\n'
        f'  e.onload=initFreshChat,i.head.appendChild(e));\n'
        f'}}\n'
        f'function initiateCall(){{initialize(document,"freshchat-js-sdk")}}\n'
        f'window.addEventListener?window.addEventListener("load",initiateCall,!1):window.attachEvent("load",initiateCall,!1);'
    ))


# ──────────────────────────────────────────────────────────────────────────────
#  Dispatcher — mapping slug → builder function
# ──────────────────────────────────────────────────────────────────────────────

INTEGRATION_BUILDERS: dict[str, callable] = {
    "google_analytics": build_google_analytics,
    "google_tag_manager": build_google_tag_manager,
    "matomo": build_matomo,
    "plausible": build_plausible,
    "clarity": build_clarity,
    "hotjar": build_hotjar,
    "mixpanel": build_mixpanel,
    "amplitude": build_amplitude,
    "posthog": build_posthog,
    "umami": build_umami,
    "fathom": build_fathom,
    "segment": build_segment,
    "heap": build_heap,
    "fullstory": build_fullstory,
    "cloudflare_web_analytics": build_cloudflare_web_analytics,
    "meta_pixel": build_meta_pixel,
    "linkedin_insight": build_linkedin_insight,
    "tiktok_pixel": build_tiktok_pixel,
    "twitter_pixel": build_twitter_pixel,
    "pinterest_tag": build_pinterest_tag,
    "snapchat_pixel": build_snapchat_pixel,
    "reddit_pixel": build_reddit_pixel,
    "quora_pixel": build_quora_pixel,
    "crisp": build_crisp,
    "intercom": build_intercom,
    "hubspot": build_hubspot,
    "zendesk": build_zendesk,
    "tidio": build_tidio,
    "brevo": build_brevo,
    "freshchat": build_freshchat,
}


def build_integration_js(slug: str, config: dict, category: str) -> str:
    """
    Génère le bloc JS pour une intégration donnée.
    Retourne une chaîne vide si l'intégration est inconnue ou si la config est invalide.
    """
    builder = INTEGRATION_BUILDERS.get(slug)
    if builder is None:
        return ""
    try:
        return builder(config, category)
    except Exception:
        return ""


def get_gtm_noscript(config: dict) -> str:
    """
    Retourne le noscript GTM pour {% cookiekit_body %}.
    Utilisé séparément car injecté en body, pas en head.
    """
    cid = config.get("container_id", "")
    if not re.match(r'^GTM-[A-Z0-9]+$', cid):
        return ""
    return (
        f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={cid}" '
        f'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
    )
