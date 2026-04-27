"""
Script temporaire : ajoute 42 nouvelles intégrations dans integrations.py
"""
import pathlib

path = pathlib.Path("/Users/espritfurtifx/Library/Mobile Documents/com~apple~CloudDocs/Documents Pro/Entreprise/Xeolux/GITHUB/package xeolux/xeolux-cookiekit/xeolux_cookiekit/integrations.py")
content = path.read_text()

# ── 1. Nouvelles entrées INTEGRATION_CATALOG ─────────────────────────────────

NEW_CATALOG = r"""
    # ── Analytics supplémentaires ──────────────────────────────────────────────

    "simple_analytics": {
        "label": "Simple Analytics",
        "category": "analytics",
        "order": 33,
        "fields": {
            "hostname": {
                "label": "Hostname (optionnel)",
                "help": "Laissez vide pour utiliser le domaine courant",
                "placeholder": "monsite.com",
            }
        },
    },

    "clicky": {
        "label": "Clicky",
        "category": "analytics",
        "order": 34,
        "fields": {
            "site_id": {
                "label": "Site ID",
                "help": "Exemple : 101234567 (Preferences → Site Settings)",
            }
        },
    },

    "statcounter": {
        "label": "StatCounter",
        "category": "analytics",
        "order": 35,
        "fields": {
            "project": {
                "label": "Project ID",
                "help": "Exemple : 12345678",
            },
            "security": {
                "label": "Security Code",
                "help": "Code de sécurité du projet StatCounter",
            },
        },
    },

    "woopra": {
        "label": "Woopra",
        "category": "analytics",
        "order": 36,
        "fields": {
            "domain": {
                "label": "Domaine",
                "help": "Exemple : monsite.com",
                "placeholder": "monsite.com",
            }
        },
    },

    "countly": {
        "label": "Countly",
        "category": "analytics",
        "order": 37,
        "fields": {
            "app_key": {
                "label": "App Key",
                "help": "Trouvé dans Management → Applications → App Key",
            },
            "server_url": {
                "label": "Server URL",
                "help": "Exemple : https://analytics.monsite.com",
                "placeholder": "https://analytics.monsite.com",
            },
        },
    },

    "adobe_analytics": {
        "label": "Adobe Analytics",
        "category": "analytics",
        "order": 38,
        "fields": {
            "script_url": {
                "label": "URL du script Launch/AppMeasurement",
                "help": "URL complète du script Adobe Launch ou AppMeasurement.js",
                "placeholder": "https://assets.adobedtm.com/...",
            }
        },
    },

    "piwik_pro": {
        "label": "Piwik PRO",
        "category": "analytics",
        "order": 39,
        "fields": {
            "container_id": {
                "label": "Container ID (UUID)",
                "help": "UUID du container dans Administration → Sites & Apps",
            },
            "container_url": {
                "label": "Container URL",
                "help": "Exemple : https://monorg.piwik.pro",
                "placeholder": "https://monorg.piwik.pro",
            },
        },
    },

    # ── Session replay / heatmaps ──────────────────────────────────────────────

    "smartlook": {
        "label": "Smartlook",
        "category": "analytics",
        "order": 50,
        "fields": {
            "project_key": {
                "label": "Project Key",
                "help": "Trouvé dans Settings → Project → Project Key",
            }
        },
    },

    "mouseflow": {
        "label": "Mouseflow",
        "category": "analytics",
        "order": 51,
        "fields": {
            "website_id": {
                "label": "Website ID (UUID)",
                "help": "UUID dans Settings → Tracking Code",
            }
        },
    },

    "crazy_egg": {
        "label": "Crazy Egg",
        "category": "analytics",
        "order": 52,
        "fields": {
            "account_number": {
                "label": "Account Number",
                "help": "Exemple : 00112233 (visible dans le snippet de suivi)",
            }
        },
    },

    "lucky_orange": {
        "label": "Lucky Orange",
        "category": "analytics",
        "order": 53,
        "fields": {
            "site_id": {
                "label": "Site ID",
                "help": "Exemple : 123456 (Settings → Tracking Code)",
            }
        },
    },

    "logrocket": {
        "label": "LogRocket",
        "category": "analytics",
        "order": 54,
        "fields": {
            "app_id": {
                "label": "App ID",
                "help": "Format : org/app (ex : monorg/monapp)",
                "placeholder": "monorg/monapp",
            }
        },
    },

    "pendo": {
        "label": "Pendo",
        "category": "analytics",
        "order": 55,
        "fields": {
            "api_key": {
                "label": "API Key",
                "help": "Trouvé dans Settings → Subscription Settings → API Keys",
            }
        },
    },

    "kissmetrics": {
        "label": "Kissmetrics",
        "category": "analytics",
        "order": 56,
        "fields": {
            "api_key": {
                "label": "API Key",
                "help": "Trouvé dans Settings → API Keys",
            }
        },
    },

    "openreplay": {
        "label": "OpenReplay",
        "category": "analytics",
        "order": 57,
        "fields": {
            "project_key": {
                "label": "Project Key",
                "help": "Trouvé dans Preferences → Project → Project Key",
            },
            "ingest_point": {
                "label": "Ingest Point (optionnel — auto-hébergé)",
                "help": "URL de votre instance (ex : https://openreplay.monsite.com/ingest)",
                "placeholder": "https://openreplay.monsite.com/ingest",
            },
        },
    },

    "inspectlet": {
        "label": "Inspectlet",
        "category": "analytics",
        "order": 58,
        "fields": {
            "wid": {
                "label": "Website ID",
                "help": "Exemple : 1234567890 (dans Install Code)",
            }
        },
    },

    # ── Marketing pixels supplémentaires ──────────────────────────────────────

    "google_ads": {
        "label": "Google Ads — Balise de conversion",
        "category": "marketing",
        "order": 100,
        "fields": {
            "conversion_id": {
                "label": "Conversion ID",
                "help": "Exemple : AW-123456789",
                "placeholder": "AW-123456789",
            },
            "conversion_label": {
                "label": "Conversion Label (optionnel)",
                "help": "Ex : AbCdEfGhIjKlMnOp (pour un événement spécifique)",
            },
        },
    },

    "microsoft_uet": {
        "label": "Microsoft Advertising — UET Tag",
        "category": "marketing",
        "order": 101,
        "fields": {
            "tag_id": {
                "label": "Tag ID",
                "help": "Exemple : 123456789 (Conversion Tracking → UET Tag)",
            }
        },
    },

    "criteo": {
        "label": "Criteo OneTag",
        "category": "marketing",
        "order": 102,
        "fields": {
            "account_id": {
                "label": "Account ID",
                "help": "Exemple : 12345 (Criteo Dashboard → Publisher Account ID)",
            }
        },
    },

    "adroll": {
        "label": "AdRoll Pixel",
        "category": "marketing",
        "order": 103,
        "fields": {
            "adroll_adv_id": {
                "label": "Advertiser ID (adv_id)",
                "help": "Exemple : ABCDEFGHIJKLMNO (Dashboard → Pixel → Setup)",
            },
            "adroll_pix_id": {
                "label": "Pixel ID (pix_id)",
                "help": "Exemple : PQRSTUVWXYZ",
            },
        },
    },

    "the_trade_desk": {
        "label": "The Trade Desk — Universal Pixel",
        "category": "marketing",
        "order": 104,
        "fields": {
            "advertiser_id": {
                "label": "Advertiser ID",
                "help": "Exemple : abc123def (TTD → Pixels → Advertiser ID)",
            }
        },
    },

    "taboola": {
        "label": "Taboola Pixel",
        "category": "marketing",
        "order": 105,
        "fields": {
            "account_id": {
                "label": "Account ID",
                "help": "Exemple : monsite (Taboola Ads → Pixel)",
            }
        },
    },

    "outbrain": {
        "label": "Outbrain Pixel",
        "category": "marketing",
        "order": 106,
        "fields": {
            "account_id": {
                "label": "Account ID / OB User Token",
                "help": "Exemple : abcdefg1234567890 (Outbrain Amplify → Pixel)",
            }
        },
    },

    "amazon_ads": {
        "label": "Amazon Ads — Insight Tag",
        "category": "marketing",
        "order": 107,
        "fields": {
            "advertiser_id": {
                "label": "Advertiser ID",
                "help": "Exemple : ENTITY1234567890 (Amazon Ads → Insight Tag)",
            }
        },
    },

    "klaviyo": {
        "label": "Klaviyo",
        "category": "marketing",
        "order": 110,
        "fields": {
            "public_api_key": {
                "label": "Public API Key (Site ID)",
                "help": "Exemple : Ab12Cd (Account → Settings → API Keys)",
            }
        },
    },

    "mailchimp": {
        "label": "Mailchimp Web Tracking",
        "category": "marketing",
        "order": 111,
        "fields": {
            "u": {
                "label": "User ID (u)",
                "help": "Paramètre 'u' du snippet Mailchimp",
            },
            "id": {
                "label": "List ID (id)",
                "help": "Paramètre 'id' du snippet Mailchimp",
            },
        },
    },

    "activecampaign": {
        "label": "ActiveCampaign Site Tracking",
        "category": "marketing",
        "order": 112,
        "fields": {
            "account_id": {
                "label": "Account ID",
                "help": "Trouvé dans Settings → Tracking → Site Tracking",
            },
            "tracking_url": {
                "label": "Tracking URL",
                "help": "Exemple : https://moncompte.activehosted.com",
                "placeholder": "https://moncompte.activehosted.com",
            },
        },
    },

    "customer_io": {
        "label": "Customer.io Tracking",
        "category": "marketing",
        "order": 113,
        "fields": {
            "site_id": {
                "label": "Site ID",
                "help": "Trouvé dans Settings → API Credentials → Site ID",
            }
        },
    },

    # ── Chat supplémentaires ───────────────────────────────────────────────────

    "livechat": {
        "label": "LiveChat",
        "category": "preferences",
        "order": 70,
        "fields": {
            "license": {
                "label": "License Number",
                "help": "Exemple : 1234567 (Settings → Chat widget → Installation)",
            }
        },
    },

    "drift": {
        "label": "Drift",
        "category": "preferences",
        "order": 71,
        "fields": {
            "embed_id": {
                "label": "Embed ID",
                "help": "Trouvé dans Settings → App Settings → Installation",
            }
        },
    },

    "tawkto": {
        "label": "tawk.to",
        "category": "preferences",
        "order": 72,
        "fields": {
            "property_id": {
                "label": "Property ID / Widget ID",
                "help": "Format : propertyId/widgetId (Administration → Chat Widget)",
                "placeholder": "5e1234abcdef12/default",
            }
        },
    },

    "smartsupp": {
        "label": "Smartsupp",
        "category": "preferences",
        "order": 73,
        "fields": {
            "key": {
                "label": "Chat Key",
                "help": "Exemple : abc123def456 (Account → Chat Box → Installation)",
            }
        },
    },

    "olark": {
        "label": "Olark",
        "category": "preferences",
        "order": 74,
        "fields": {
            "site_id": {
                "label": "Site ID",
                "help": "Format : XXXX-XXX-XX-XXXX (Account → Installation)",
                "placeholder": "XXXX-XXX-XX-XXXX",
            }
        },
    },

    # ── CDP / Data routing ─────────────────────────────────────────────────────

    "rudderstack": {
        "label": "RudderStack",
        "category": "analytics",
        "order": 80,
        "fields": {
            "write_key": {
                "label": "Write Key",
                "help": "Source Write Key dans RudderStack → Sources",
            },
            "data_plane_url": {
                "label": "Data Plane URL",
                "help": "Exemple : https://hosted.rudderlabs.com",
                "placeholder": "https://hosted.rudderlabs.com",
            },
        },
    },

    "snowplow": {
        "label": "Snowplow Analytics",
        "category": "analytics",
        "order": 81,
        "fields": {
            "collector_url": {
                "label": "Collector URL (sans https://)",
                "help": "Exemple : collector.monsite.com",
                "placeholder": "collector.monsite.com",
            },
            "app_id": {
                "label": "App ID (optionnel)",
                "help": "Identifiant de votre application Snowplow",
            },
        },
    },

    # ── A/B testing ────────────────────────────────────────────────────────────

    "optimizely": {
        "label": "Optimizely Web",
        "category": "analytics",
        "order": 85,
        "fields": {
            "project_id": {
                "label": "Project ID",
                "help": "Exemple : 1234567890 (Settings → Project → Project ID)",
            }
        },
    },

    "vwo": {
        "label": "VWO (Visual Website Optimizer)",
        "category": "analytics",
        "order": 86,
        "fields": {
            "account_id": {
                "label": "Account ID",
                "help": "Exemple : 123456 (VWO → Settings → Account ID)",
            }
        },
    },

    "ab_tasty": {
        "label": "AB Tasty",
        "category": "analytics",
        "order": 87,
        "fields": {
            "account_id": {
                "label": "Account ID",
                "help": "Exemple : abc123def (AB Tasty → Settings → Tracking ID)",
            }
        },
    },

    "growthbook": {
        "label": "GrowthBook",
        "category": "analytics",
        "order": 88,
        "fields": {
            "client_key": {
                "label": "Client Key",
                "help": "Exemple : sdk-abc123 (GrowthBook → SDK Configuration)",
                "placeholder": "sdk-abc123",
            },
            "api_host": {
                "label": "API Host (optionnel — self-hosted)",
                "help": "Par défaut : https://cdn.growthbook.io",
                "placeholder": "https://cdn.growthbook.io",
            },
        },
    },

    # ── Push notifications ─────────────────────────────────────────────────────

    "onesignal": {
        "label": "OneSignal",
        "category": "preferences",
        "order": 90,
        "fields": {
            "app_id": {
                "label": "App ID (UUID)",
                "help": "Settings → Keys & IDs → OneSignal App ID",
            }
        },
    },

    "pushengage": {
        "label": "PushEngage",
        "category": "preferences",
        "order": 91,
        "fields": {
            "api_key": {
                "label": "Site API Key",
                "help": "PushEngage Dashboard → Settings → Site Settings",
            }
        },
    },

"""

# ── 2. Nouvelles build functions ──────────────────────────────────────────────

NEW_BUILD_FUNCTIONS = r"""

# ── Analytics supplémentaires ──────────────────────────────────────────────────

def build_simple_analytics(cfg: dict, category: str) -> str:
    hostname = cfg.get("hostname", "")
    if hostname and not re.match(r'^[a-zA-Z0-9._-]+$', hostname):
        return ""
    return _wrap(category, (
        '(function(){\n'
        '  var s=document.createElement("script");\n'
        '  s.defer=true;\n'
        '  s.src="https://scripts.simpleanalyticscdn.com/latest.js";\n'
        + ('  s.setAttribute("data-hostname","' + hostname + '");\n' if hostname else '')
        + '  document.head.appendChild(s);\n'
        '})();'
    ))


def build_clicky(cfg: dict, category: str) -> str:
    site_id = str(cfg.get("site_id", ""))
    if not re.match(r'^\d+$', site_id):
        return ""
    return _wrap(category, (
        f'var clicky_site_ids=clicky_site_ids||[];clicky_site_ids.push({site_id});\n'
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="//static.getclicky.com/js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_statcounter(cfg: dict, category: str) -> str:
    project = str(cfg.get("project", ""))
    security = cfg.get("security", "")
    if not re.match(r'^\d+$', project):
        return ""
    if not re.match(r'^\w+$', security):
        return ""
    return _wrap(category, (
        f'var sc_project={project};\n'
        f'var sc_invisible=1;\n'
        f'var sc_security="{security}";\n'
        f'(function(){{\n'
        f'  var sc=document.createElement("script");sc.async=true;\n'
        f'  sc.src="https://www.statcounter.com/counter/counter.js";\n'
        f'  document.head.appendChild(sc);\n'
        f'}})();'
    ))


def build_woopra(cfg: dict, category: str) -> str:
    domain = cfg.get("domain", "")
    if not re.match(r'^[a-zA-Z0-9._-]+$', domain):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  (function(c,s,u,n){{c[u]=c[u]||{{}};c[u].accts=n;\n'
        f'  var w=document,d=w.createElement(s),j=w.getElementsByTagName(s)[0];\n'
        f'  d.async=true;d.src="https://static.woopra.com/js/w.js";\n'
        f'  j.parentNode.insertBefore(d,j);\n'
        f'  }})(window,"script","woopra",["{domain}"]);\n'
        f'}})();'
    ))


def build_countly(cfg: dict, category: str) -> str:
    app_key = cfg.get("app_key", "")
    server_url = cfg.get("server_url", "").rstrip("/")
    if not re.match(r'^[a-zA-Z0-9]+$', app_key):
        return ""
    if not server_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'var Countly=Countly||{{}};\n'
        f'Countly.q=Countly.q||[];\n'
        f'Countly.app_key="{app_key}";\n'
        f'Countly.url="{server_url}";\n'
        f'Countly.q.push(["track_sessions"]);\n'
        f'Countly.q.push(["track_pageview"]);\n'
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="{server_url}/sdk/web/countly.min.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_adobe_analytics(cfg: dict, category: str) -> str:
    script_url = cfg.get("script_url", "")
    if not script_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="{script_url}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_piwik_pro(cfg: dict, category: str) -> str:
    container_id = cfg.get("container_id", "")
    container_url = cfg.get("container_url", "").rstrip("/")
    if not re.match(r'^[0-9a-f-]{36}$', container_id.lower()):
        return ""
    if not container_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(window,document,dataLayerName,id){{\n'
        f'  window[dataLayerName]=window[dataLayerName]||[];\n'
        f'  window[dataLayerName].push({{start:(new Date).getTime(),event:"stg.start"}});\n'
        f'  var scripts=document.getElementsByTagName("script")[0],\n'
        f'  tags=document.createElement("script");\n'
        f'  tags.async=true;\n'
        f'  tags.src="{container_url}/containers/{container_id}.js";\n'
        f'  scripts.parentNode.insertBefore(tags,scripts);\n'
        f'}})(window,document,"dataLayer","{container_id}");'
    ))


# ── Session replay / heatmaps ──────────────────────────────────────────────────

def build_smartlook(cfg: dict, category: str) -> str:
    key = cfg.get("project_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', key):
        return ""
    return _wrap(category, (
        f'window.smartlook||(function(d){{\n'
        f'  var o=smartlook=function(){{o.api.push(arguments)}},\n'
        f'  h=d.getElementsByTagName("head")[0];\n'
        f'  var c=d.createElement("script");o.api=new Array();\n'
        f'  c.async=true;c.type="text/javascript";c.charset="utf-8";\n'
        f'  c.src="https://web-sdk.smartlook.com/recorder.js";\n'
        f'  h.appendChild(c);\n'
        f'}})(document);\n'
        f'smartlook("init","{key}",{{region:"eu"}});'
    ))


def build_mouseflow(cfg: dict, category: str) -> str:
    website_id = cfg.get("website_id", "")
    if not re.match(r'^[0-9a-f-]{36}$', website_id.lower()):
        return ""
    return _wrap(category, (
        f'window._mfq=window._mfq||[];\n'
        f'(function(){{\n'
        f'  var mf=document.createElement("script");\n'
        f'  mf.type="text/javascript";mf.defer=true;\n'
        f'  mf.src="//cdn.mouseflow.com/projects/{website_id}.js";\n'
        f'  document.getElementsByTagName("head")[0].appendChild(mf);\n'
        f'}})();'
    ))


def build_crazy_egg(cfg: dict, category: str) -> str:
    account = str(cfg.get("account_number", ""))
    if not re.match(r'^\d+$', account):
        return ""
    account_padded = account.zfill(8)
    p1, p2 = account_padded[:4], account_padded[4:]
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://script.crazyegg.com/pages/scripts/{p1}/{p2}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_lucky_orange(cfg: dict, category: str) -> str:
    site_id = str(cfg.get("site_id", ""))
    if not re.match(r'^\d+$', site_id):
        return ""
    return _wrap(category, (
        f'window.__lo_site_id={site_id};\n'
        f'(function(){{\n'
        f'  var wa=document.createElement("script");\n'
        f'  wa.type="text/javascript";wa.async=true;\n'
        f'  wa.src="https://d10lpsik1i8c69.cloudfront.net/w.js";\n'
        f'  var s=document.getElementsByTagName("script")[0];\n'
        f'  s.parentNode.insertBefore(wa,s);\n'
        f'}})();'
    ))


def build_logrocket(cfg: dict, category: str) -> str:
    app_id = cfg.get("app_id", "")
    if not re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$', app_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://cdn.lr-ingest.com/LogRocket.min.js";\n'
        f'  s.crossOrigin="anonymous";\n'
        f'  s.onload=function(){{LogRocket.init("{app_id}");}}\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_pendo(cfg: dict, category: str) -> str:
    api_key = cfg.get("api_key", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return ""
    return _wrap(category, (
        f'(function(apiKey){{\n'
        f'  (function(p,e,n,d,o){{\n'
        f'    var v,w,x,y,z;o=p[d]=p[d]||{{}};\n'
        f'    o._q=o._q||[];\n'
        f'    v=["initialize","identify","updateOptions","pageLoad","track"];\n'
        f'    for(w=0,x=v.length;w<x;++w)(function(m){{\n'
        f'      o[m]=o[m]||function(){{o._q[m===v[0]?"unshift":"push"]([m].concat([].slice.call(arguments,0)))}}\n'
        f'    }})(v[w]);\n'
        f'    y=e.createElement(n);y.async=true;\n'
        f'    y.src="https://cdn.pendo.io/agent/static/"+apiKey+"/pendo.js";\n'
        f'    z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);\n'
        f'  }})(window,document,"script","pendo");\n'
        f'}})(\\"{api_key}\\");'
    ))


def build_kissmetrics(cfg: dict, category: str) -> str:
    api_key = cfg.get("api_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', api_key):
        return ""
    return _wrap(category, (
        f'var _kmq=_kmq||[];\n'
        f'(function(){{\n'
        f'  var km=document.createElement("script");\n'
        f'  km.type="text/javascript";km.async=true;\n'
        f'  km.src="//i.kissmetrics.io/i.js";\n'
        f'  var s=document.getElementsByTagName("script")[0];\n'
        f'  s.parentNode.insertBefore(km,s);\n'
        f'  var km2=document.createElement("script");\n'
        f'  km2.type="text/javascript";km2.async=true;\n'
        f'  km2.src="//scripts.kissmetrics.io/{api_key}.2.js";\n'
        f'  s.parentNode.insertBefore(km2,s);\n'
        f'}})();'
    ))


def build_openreplay(cfg: dict, category: str) -> str:
    project_key = cfg.get("project_key", "")
    ingest_point = cfg.get("ingest_point", "")
    if not re.match(r'^[a-zA-Z0-9]+$', project_key):
        return ""
    if ingest_point and not ingest_point.startswith("https://"):
        return ""
    opts = f'{{projectKey:"{project_key}",ingestPoint:"{ingest_point}"}}' if ingest_point else f'{{projectKey:"{project_key}"}}'
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://static.openreplay.com/latest/openreplay.js";\n'
        f'  s.onload=function(){{\n'
        f'    var tracker=new OpenReplay({opts});\n'
        f'    tracker.start();\n'
        f'  }};\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_inspectlet(cfg: dict, category: str) -> str:
    wid = str(cfg.get("wid", ""))
    if not re.match(r'^\d+$', wid):
        return ""
    return _wrap(category, (
        f'window.__insp=window.__insp||[];\n'
        f'__insp.push(["wid",{wid}]);\n'
        f'(function(){{\n'
        f'  if(typeof window.__inspld!="undefined")return;\n'
        f'  window.__inspld=1;\n'
        f'  var insp=document.createElement("script");\n'
        f'  insp.type="text/javascript";insp.async=true;\n'
        f'  insp.src=("https:"==document.location.protocol?"https":"http")+"://cdn.inspectlet.com/inspectlet.js?wid={wid}&r="+Math.floor(new Date().getTime()/3600000);\n'
        f'  var x=document.getElementsByTagName("script")[0];\n'
        f'  x.parentNode.insertBefore(insp,x);\n'
        f'}})();'
    ))


# ── Marketing pixels supplémentaires ──────────────────────────────────────────

def build_google_ads(cfg: dict, category: str) -> str:
    conv_id = cfg.get("conversion_id", "")
    conv_label = cfg.get("conversion_label", "")
    if not re.match(r'^AW-\d+$', conv_id):
        return ""
    if conv_label and not re.match(r'^[a-zA-Z0-9_-]+$', conv_label):
        return ""
    track_line = (
        f'gtag("event","conversion",{{"send_to":"{conv_id}/{conv_label}"}});\n'
        if conv_label else ""
    )
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://www.googletagmanager.com/gtag/js?id={conv_id}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();\n'
        f'window.dataLayer=window.dataLayer||[];\n'
        f'function gtag(){{dataLayer.push(arguments);}}\n'
        f'window.gtag=gtag;\n'
        f'gtag("js",new Date());\n'
        f'gtag("config","{conv_id}");\n'
        + track_line
    ))


def build_microsoft_uet(cfg: dict, category: str) -> str:
    tag_id = str(cfg.get("tag_id", ""))
    if not re.match(r'^\d+$', tag_id):
        return ""
    return _wrap(category, (
        f'(function(w,d,t,r,u){{\n'
        f'  var f,n,i;\n'
        f'  w[u]=w[u]||[];\n'
        f'  f=function(){{var o={{ti:"{tag_id}",enableAutoSpaTracking:true}};\n'
        f'    o.q=w[u];w[u]=new UET(o);w[u].push("pageLoad");}};\n'
        f'  n=d.createElement(t);n.src=r;n.async=1;\n'
        f'  n.onload=n.onreadystatechange=function(){{\n'
        f'    var s=this.readyState;\n'
        f'    s&&s!=="loaded"&&s!=="complete"||(f(),n.onload=n.onreadystatechange=null);\n'
        f'  }};\n'
        f'  i=d.getElementsByTagName(t)[0];i.parentNode.insertBefore(n,i);\n'
        f'}})(window,document,"script","//bat.bing.com/bat.js","uetq");'
    ))


def build_criteo(cfg: dict, category: str) -> str:
    account_id = str(cfg.get("account_id", ""))
    if not re.match(r'^\d+$', account_id):
        return ""
    return _wrap(category, (
        f'window.criteo_q=window.criteo_q||[];\n'
        f'var deviceType=/iPad/.test(navigator.userAgent)?"t":/Mobile|iP(hone|od)|Android|BlackBerry|IEMobile|Silk/.test(navigator.userAgent)?"m":"d";\n'
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://static.criteo.net/js/ld/ld.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();\n'
        f'window.criteo_q.push(\n'
        f'  {{event:"setAccount",account:{account_id}}},\n'
        f'  {{event:"setSiteType",type:deviceType}},\n'
        f'  {{event:"viewPage"}}\n'
        f');'
    ))


def build_adroll(cfg: dict, category: str) -> str:
    adv_id = cfg.get("adroll_adv_id", "")
    pix_id = cfg.get("adroll_pix_id", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', adv_id):
        return ""
    if not re.match(r'^[a-zA-Z0-9_-]+$', pix_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  window.adroll_adv_id="{adv_id}";\n'
        f'  window.adroll_pix_id="{pix_id}";\n'
        f'  window.adroll_version="2.0";\n'
        f'  var s=document.createElement("script");\n'
        f'  s.async=true;s.type="text/javascript";\n'
        f'  s.src="https://s.adroll.com/j/roundtrip.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_the_trade_desk(cfg: dict, category: str) -> str:
    advertiser_id = cfg.get("advertiser_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', advertiser_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var img=document.createElement("img");\n'
        f'  img.height=1;img.width=1;\n'
        f'  img.style.cssText="border-style:none;";\n'
        f'  img.alt="";\n'
        f'  img.src="https://insight.adsrvr.org/track/up?adv={advertiser_id}&ct=0:u0zk1x6&fmt=3";\n'
        f'  document.body.appendChild(img);\n'
        f'}})();'
    ))


def build_taboola(cfg: dict, category: str) -> str:
    account_id = cfg.get("account_id", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', account_id):
        return ""
    return _wrap(category, (
        f'window._tfa=window._tfa||[];\n'
        f'window._tfa.push({{notify:"event",name:"page_view",id:"{account_id}"}});\n'
        f'!function(t,f,a,x){{\n'
        f'  if(!document.getElementById(x)){{\n'
        f'    t.async=1;t.src=a;t.id=x;\n'
        f'    f.parentNode.insertBefore(t,f);\n'
        f'  }}\n'
        f'}}(document.createElement("script"),\n'
        f'document.getElementsByTagName("script")[0],\n'
        f'"//cdn.taboola.com/libtrc/unip/{account_id}/tfa.js","tb_tfa_script");'
    ))


def build_outbrain(cfg: dict, category: str) -> str:
    account_id = cfg.get("account_id", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', account_id):
        return ""
    return _wrap(category, (
        f'!function(_window,_document){{\n'
        f'  var OB_ADV_ID="{account_id}";\n'
        f'  if(_window.obApi){{\n'
        f'    var toArray=function(o){{return Object.prototype.toString.call(o)==="[object Array]"?o:[o];}};\n'
        f'    _window.obApi.marketerId=toArray(_window.obApi.marketerId).concat(toArray(OB_ADV_ID));\n'
        f'    return;\n'
        f'  }}\n'
        f'  var api=_window.obApi=function(){{api.dispatch?api.dispatch.apply(api,arguments):api.queue.push(arguments);}};\n'
        f'  api.version="1.1";api.loaded=true;api.marketerId=OB_ADV_ID;api.queue=[];\n'
        f'  var tag=_document.createElement("script");tag.async=true;\n'
        f'  tag.src="https://amplify.outbrain.com/cp/obtp.js";tag.referrerPolicy="unsafe-url";\n'
        f'  var script=_document.getElementsByTagName("script")[0];\n'
        f'  script.parentNode.insertBefore(tag,script);\n'
        f'}}(window,document);\n'
        f'obApi("track","PAGE_VIEW");'
    ))


def build_amazon_ads(cfg: dict, category: str) -> str:
    advertiser_id = cfg.get("advertiser_id", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', advertiser_id):
        return ""
    return _wrap(category, (
        f'!function(a9,a,p,s,t,A,g){{\n'
        f'  if(a[a9])return;\n'
        f'  function q(c,r){{a[a9]._Q.push([c,r])}}\n'
        f'  a[a9]={{init:function(){{}},fetchBids:function(){{}},setDisplayBids:function(){{}},\n'
        f'  targetingKeys:function(){{return[]}},_Q:[]}};\n'
        f'  A=p.createElement(s);A.async=true;A.src=t;\n'
        f'  g=p.getElementsByTagName(s)[0];g.parentNode.insertBefore(A,g);\n'
        f'  window.amzn_targs=window.amzn_targs||[];\n'
        f'  window.amzn_targs.push("{advertiser_id}");\n'
        f'}}("apstag",window,document,"script","https://c.amazon-adsystem.com/aax2/apstag.js");'
    ))


def build_klaviyo(cfg: dict, category: str) -> str:
    public_api_key = cfg.get("public_api_key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', public_api_key):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.type="text/javascript";\n'
        f'  s.src="https://static.klaviyo.com/onsite/js/klaviyo.js?company_id={public_api_key}";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_mailchimp(cfg: dict, category: str) -> str:
    u = cfg.get("u", "")
    list_id = cfg.get("id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', u):
        return ""
    if not re.match(r'^[a-zA-Z0-9]+$', list_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://chimpstatic.com/mcjs-connected/js/users/{u}/{list_id}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_activecampaign(cfg: dict, category: str) -> str:
    account_id = str(cfg.get("account_id", ""))
    tracking_url = cfg.get("tracking_url", "").rstrip("/")
    if not re.match(r'^\d+$', account_id):
        return ""
    if not tracking_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(e,t,o,n,p,r,i){{\n'
        f'  e.visitorGlobalObjectAlias=n;\n'
        f'  e[e.visitorGlobalObjectAlias]=e[e.visitorGlobalObjectAlias]||function(){{\n'
        f'    (e[e.visitorGlobalObjectAlias].q=e[e.visitorGlobalObjectAlias].q||[]).push(arguments);\n'
        f'  }};\n'
        f'  e[e.visitorGlobalObjectAlias].l=(new Date).getTime();\n'
        f'  r=t.createElement("script");r.src=o;r.async=true;\n'
        f'  i=t.getElementsByTagName("script")[0];i.parentNode.insertBefore(r,i);\n'
        f'}})(window,document,"{tracking_url}/acton/core/{account_id}/visitor.js","vgo");\n'
        f'vgo("setAccount","{account_id}");\n'
        f'vgo("setTrackByDefault",true);\n'
        f'vgo("process");'
    ))


def build_customer_io(cfg: dict, category: str) -> str:
    site_id = cfg.get("site_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', site_id):
        return ""
    return _wrap(category, (
        f'var _cio=_cio||[];\n'
        f'(function(){{\n'
        f'  var a,b,c;\n'
        f'  a=function(f){{return function(){{\n'
        f'    _cio.push([f].concat(Array.prototype.slice.call(arguments,0)))\n'
        f'  }}}}\n'
        f'  b=["load","identify","sidentify","track","page"];\n'
        f'  for(c=0;c<b.length;c++){{_cio[b[c]]=a(b[c]);}}\n'
        f'  var t=document.createElement("script"),s=document.getElementsByTagName("script")[0];\n'
        f'  t.async=true;t.id="cio-tracker";\n'
        f'  t.setAttribute("data-site-id","{site_id}");\n'
        f'  t.src="https://assets.customer.io/assets/track.js";\n'
        f'  s.parentNode.insertBefore(t,s);\n'
        f'}})();'
    ))


# ── Chat supplémentaires ───────────────────────────────────────────────────────

def build_livechat(cfg: dict, category: str) -> str:
    license_id = str(cfg.get("license", ""))
    if not re.match(r'^\d+$', license_id):
        return ""
    return _wrap(category, (
        f'window.__lc=window.__lc||{{}};\n'
        f'window.__lc.license={license_id};\n'
        f'(function(n,t,c){{\n'
        f'  function i(n){{return e._h?e._h.apply(null,n):e.queue.push(n)}}\n'
        f'  var e={{queue:[],call:function(){{i(["call",Array.prototype.slice.call(arguments)])}},\n'
        f'  on:function(){{i(["on",Array.prototype.slice.call(arguments)])}},\n'
        f'  get:function(){{if(!e._h)throw new Error("LiveChatWidget.get can only be called after plugins are loaded");\n'
        f'    return i(["get",Array.prototype.slice.call(arguments)]);}},\n'
        f'  _h:null,_q:[]}};\n'
        f'  t[n]=e;\n'
        f'  var r=document.createElement("script");r.async=true;\n'
        f'  r.type="text/javascript";\n'
        f'  r.src="https://cdn.livechatinc.com/tracking.js";\n'
        f'  document.head.appendChild(r);\n'
        f'}}("LiveChatWidget",window));'
    ))


def build_drift(cfg: dict, category: str) -> str:
    embed_id = cfg.get("embed_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', embed_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var t=window.driftt=window.drift=window.driftt||[];\n'
        f'  if(!t.init){{\n'
        f'    if(t.invoked){{window.console&&console.error&&console.error("Drift snippet included twice.");}}\n'
        f'    else{{\n'
        f'      t.invoked=true;\n'
        f'      t.methods=["identify","config","track","reset","debug","show","ping","page","hide","off","on"];\n'
        f'      t.factory=function(e){{return function(){{\n'
        f'        var n=Array.prototype.slice.call(arguments);\n'
        f'        return n.unshift(e),t.push(n),t}}}};\n'
        f'      for(var e=0;e<t.methods.length;e++){{\n'
        f'        var n=t.methods[e];t[n]=t.factory(n);\n'
        f'      }}\n'
        f'      t.load=function(e){{\n'
        f'        var n=3e5,o=Math.ceil(new Date()/n)*n,\n'
        f'        i=document.createElement("script");\n'
        f'        i.type="text/javascript";i.async=true;i.crossorigin="anonymous";\n'
        f'        i.src="https://js.driftt.com/include/"+o+"/"+e+".js";\n'
        f'        var a=document.getElementsByTagName("script")[0];\n'
        f'        a.parentNode.insertBefore(i,a);\n'
        f'      }};t.SNIPPET_VERSION="0.3.1";t.load("{embed_id}");\n'
        f'    }}\n'
        f'  }}\n'
        f'}})();'
    ))


def build_tawkto(cfg: dict, category: str) -> str:
    property_id = cfg.get("property_id", "")
    if not re.match(r'^[a-zA-Z0-9]+/[a-zA-Z0-9]+$', property_id):
        return ""
    parts = property_id.split("/")
    prop_id, widget_id = parts[0], parts[1]
    return _wrap(category, (
        f'var Tawk_API=Tawk_API||{{}},Tawk_LoadStart=new Date();\n'
        f'(function(){{\n'
        f'  var s1=document.createElement("script"),\n'
        f'  s0=document.getElementsByTagName("script")[0];\n'
        f'  s1.async=true;\n'
        f'  s1.src="https://embed.tawk.to/{prop_id}/{widget_id}";\n'
        f'  s1.charset="UTF-8";\n'
        f'  s1.setAttribute("crossorigin","*");\n'
        f'  s0.parentNode.insertBefore(s1,s0);\n'
        f'}})();'
    ))


def build_smartsupp(cfg: dict, category: str) -> str:
    key = cfg.get("key", "")
    if not re.match(r'^[a-zA-Z0-9]+$', key):
        return ""
    return _wrap(category, (
        f'var _smartsupp=_smartsupp||{{}};\n'
        f'window.smartsupp||(function(d){{\n'
        f'  var s,c,o=window.smartsupp=function(){{o._.push(arguments)}};\n'
        f'  o._=[];s=d.getElementsByTagName("script")[0];\n'
        f'  c=d.createElement("script");\n'
        f'  c.type="text/javascript";c.charset="utf-8";c.async=true;\n'
        f'  c.src="https://www.smartsupp.com/loader.js?key={key}";\n'
        f'  s.parentNode.insertBefore(c,s);\n'
        f'}})(document);'
    ))


def build_olark(cfg: dict, category: str) -> str:
    site_id = cfg.get("site_id", "")
    if not re.match(r'^[\d-]+$', site_id):
        return ""
    return _wrap(category, (
        f';(function(o,l,a,r,k,y){{\n'
        f'  if(o.olark)return;\n'
        f'  r="script";y=l.createElement(r);r=l.getElementsByTagName(r)[0];\n'
        f'  y.async=1;y.src="//static.olark.com/jsclient/loader0.js";\n'
        f'  r.parentNode.insertBefore(y,r);\n'
        f'  o.olark||(o.olark=function(){{\n'
        f'    o.olark._.push(arguments);\n'
        f'    if(o.olark.extend)o.olark.extend(arguments);\n'
        f'  }},o.olark.identify=function(s){{o.olark.account_id=s}},\n'
        f'  o.olark.extend=function(a){{for(var b=a.length,c=0;c<b;c++)o.olark._[c]=a[c]}},\n'
        f'  o.olark._=[]);\n'
        f'  olark.identify("{site_id}");\n'
        f'}})(window,document);'
    ))


# ── CDP / Data routing ─────────────────────────────────────────────────────────

def build_rudderstack(cfg: dict, category: str) -> str:
    write_key = cfg.get("write_key", "")
    data_plane_url = cfg.get("data_plane_url", "https://hosted.rudderlabs.com").rstrip("/")
    if not re.match(r'^[a-zA-Z0-9]+$', write_key):
        return ""
    if not data_plane_url.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  if(!window.rudderanalytics){{\n'
        f'    window.rudderanalytics=[];\n'
        f'    var methods=["load","page","track","identify","alias","group","ready","reset"];\n'
        f'    for(var i=0;i<methods.length;i++){{\n'
        f'      (function(m){{window.rudderanalytics[m]=function(){{\n'
        f'        window.rudderanalytics.push([m].concat(Array.prototype.slice.call(arguments)));\n'
        f'      }};}})(methods[i]);\n'
        f'    }}\n'
        f'    var s=document.createElement("script");s.type="text/javascript";s.async=true;\n'
        f'    s.src="https://cdn.rudderlabs.com/v1.1/rudder-analytics.min.js";\n'
        f'    var f=document.getElementsByTagName("script")[0];\n'
        f'    f.parentNode.insertBefore(s,f);\n'
        f'    rudderanalytics.load("{write_key}","{data_plane_url}");\n'
        f'    rudderanalytics.page();\n'
        f'  }}\n'
        f'}})();'
    ))


def build_snowplow(cfg: dict, category: str) -> str:
    collector_url = cfg.get("collector_url", "")
    app_id = cfg.get("app_id", "")
    if not re.match(r'^[a-zA-Z0-9._-]+$', collector_url):
        return ""
    if app_id and not re.match(r'^[a-zA-Z0-9_-]+$', app_id):
        return ""
    tracker_opts = f'{{appId:"{app_id}"}}' if app_id else '{}'
    return _wrap(category, (
        f';(function(p,l,o,w,i,n,g){{\n'
        f'  if(!p[i]){{p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];\n'
        f'  p.GlobalSnowplowNamespace.push(i);p[i]=function(){{\n'
        f'    (p[i].q=p[i].q||[]).push(arguments);}};\n'
        f'  p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];\n'
        f'  n.async=1;n.src=w;g.parentNode.insertBefore(n,g);}}\n'
        f'}}(window,document,"script","https://cdn.jsdelivr.net/npm/@snowplow/javascript-tracker@latest/dist/sp.min.js","snowplow"));\n'
        f'snowplow("newTracker","cf","{collector_url}",{tracker_opts});\n'
        f'snowplow("enableActivityTracking",10,10);\n'
        f'snowplow("trackPageView");'
    ))


# ── A/B testing ────────────────────────────────────────────────────────────────

def build_optimizely(cfg: dict, category: str) -> str:
    project_id = str(cfg.get("project_id", ""))
    if not re.match(r'^\d+$', project_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://cdn.optimizely.com/js/{project_id}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_vwo(cfg: dict, category: str) -> str:
    account_id = str(cfg.get("account_id", ""))
    if not re.match(r'^\d+$', account_id):
        return ""
    return _wrap(category, (
        f'window.VWO=window.VWO||[];\n'
        f'window.VWO.push(["activate",false]);\n'
        f'(function(){{\n'
        f'  var a=document.createElement("script");a.type="text/javascript";a.async=true;\n'
        f'  a.src="https://dev.visualwebsiteoptimizer.com/j.php?a={account_id}&u="+encodeURIComponent(document.URL)+"&f=";\n'
        f'  var b=document.getElementsByTagName("head")[0];b.appendChild(a);\n'
        f'}})();'
    ))


def build_ab_tasty(cfg: dict, category: str) -> str:
    account_id = cfg.get("account_id", "")
    if not re.match(r'^[a-zA-Z0-9]+$', account_id):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://try.abtasty.com/{account_id}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


def build_growthbook(cfg: dict, category: str) -> str:
    client_key = cfg.get("client_key", "")
    api_host = cfg.get("api_host", "https://cdn.growthbook.io") or "https://cdn.growthbook.io"
    if not re.match(r'^sdk-[a-zA-Z0-9]+$', client_key):
        return ""
    if not api_host.startswith("https://"):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="{api_host}/js/{client_key}.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
    ))


# ── Push notifications ─────────────────────────────────────────────────────────

def build_onesignal(cfg: dict, category: str) -> str:
    app_id = cfg.get("app_id", "")
    if not re.match(r'^[0-9a-f-]{36}$', app_id.lower()):
        return ""
    return _wrap(category, (
        f'window.OneSignalDeferred=window.OneSignalDeferred||[];\n'
        f'(function(){{\n'
        f'  var s=document.createElement("script");s.async=true;\n'
        f'  s.src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js";\n'
        f'  document.head.appendChild(s);\n'
        f'}})();\n'
        f'OneSignalDeferred.push(async function(OneSignal){{\n'
        f'  await OneSignal.init({{appId:"{app_id}"}});\n'
        f'}});'
    ))


def build_pushengage(cfg: dict, category: str) -> str:
    api_key = cfg.get("api_key", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return ""
    return _wrap(category, (
        f'(function(d,t){{\n'
        f'  var g=d.createElement(t),s=d.getElementsByTagName(t)[0];\n'
        f'  g.src="https://clientcdn.pushengage.com/sdks/pushengage-web-notification-script.js";\n'
        f'  g.setAttribute("data-api-key","{api_key}");\n'
        f'  g.async=true;\n'
        f'  s.parentNode.insertBefore(g,s);\n'
        f'}})(document,"script");'
    ))

"""

# ── 3. Entrées INTEGRATION_BUILDERS ──────────────────────────────────────────

NEW_DISPATCHER_ENTRIES = '''    "simple_analytics": build_simple_analytics,
    "clicky": build_clicky,
    "statcounter": build_statcounter,
    "woopra": build_woopra,
    "countly": build_countly,
    "adobe_analytics": build_adobe_analytics,
    "piwik_pro": build_piwik_pro,
    "smartlook": build_smartlook,
    "mouseflow": build_mouseflow,
    "crazy_egg": build_crazy_egg,
    "lucky_orange": build_lucky_orange,
    "logrocket": build_logrocket,
    "pendo": build_pendo,
    "kissmetrics": build_kissmetrics,
    "openreplay": build_openreplay,
    "inspectlet": build_inspectlet,
    "google_ads": build_google_ads,
    "microsoft_uet": build_microsoft_uet,
    "criteo": build_criteo,
    "adroll": build_adroll,
    "the_trade_desk": build_the_trade_desk,
    "taboola": build_taboola,
    "outbrain": build_outbrain,
    "amazon_ads": build_amazon_ads,
    "klaviyo": build_klaviyo,
    "mailchimp": build_mailchimp,
    "activecampaign": build_activecampaign,
    "customer_io": build_customer_io,
    "livechat": build_livechat,
    "drift": build_drift,
    "tawkto": build_tawkto,
    "smartsupp": build_smartsupp,
    "olark": build_olark,
    "rudderstack": build_rudderstack,
    "snowplow": build_snowplow,
    "optimizely": build_optimizely,
    "vwo": build_vwo,
    "ab_tasty": build_ab_tasty,
    "growthbook": build_growthbook,
    "onesignal": build_onesignal,
    "pushengage": build_pushengage,
'''

# ── Application des modifications ─────────────────────────────────────────────

# 1. Insérer les nouvelles entrées du catalogue
marker_catalog_end = '}\n\n\n# ─────'
if marker_catalog_end in content:
    content = content.replace(marker_catalog_end, NEW_CATALOG + '}\n\n\n# ─────', 1)
    print("✓ Catalog entries inserted")
else:
    print("✗ Catalog marker not found")
    exit(1)

# 2. Insérer les build functions avant le dispatcher
marker_dispatcher = '# ──────────────────────────────────────────────────────────────────────────────\n#  Dispatcher'
if marker_dispatcher in content:
    content = content.replace(marker_dispatcher, NEW_BUILD_FUNCTIONS + '\n' + marker_dispatcher, 1)
    print("✓ Build functions inserted")
else:
    print("✗ Dispatcher marker not found")
    exit(1)

# 3. Ajouter dans INTEGRATION_BUILDERS
marker_builders_end = '    "freshchat": build_freshchat,\n}'
if marker_builders_end in content:
    content = content.replace(
        marker_builders_end,
        '    "freshchat": build_freshchat,\n' + NEW_DISPATCHER_ENTRIES + '}',
        1
    )
    print("✓ Dispatcher entries added")
else:
    print("✗ Builders end marker not found")
    exit(1)

path.write_text(content)
print(f"✓ integrations.py updated — {content.count(chr(10))} lines")
