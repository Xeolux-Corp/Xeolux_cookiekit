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

    "visitors_now": {
        "label": "Visitors.now",
        "category": "analytics",
        "order": 33,
        "fields": {
            "token": {
                "label": "Project Token",
                "help": "Disponible dans votre tableau de bord Visitors.now",
                "placeholder": "votre_token_visitors",
            }
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


def build_visitors_now(cfg: dict, category: str) -> str:
    token = cfg.get("token", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', token):
        return ""
    return _wrap(category, (
        f'(function(){{\n'
        f'  var s=document.createElement("script");\n'
        f'  s.async=true;\n'
        f'  s.src="https://cdn.visitors.now/v.js";\n'
        f'  s.setAttribute("data-token","{token}");\n'
        f'  document.head.appendChild(s);\n'
        f'}})();'
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
    "simple_analytics": build_simple_analytics,
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
    "visitors_now": build_visitors_now,
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
