<div align="center">

# 🍪 xeolux-cookiekit

**Package Django de gestion du consentement cookies — RGPD/CNIL ready**

[![PyPI version](https://img.shields.io/pypi/v/xeolux-cookiekit.svg?color=ff6b00)](https://pypi.org/project/xeolux-cookiekit/)
[![Python](https://img.shields.io/pypi/pyversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![Django](https://img.shields.io/pypi/djversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-66%20passed-brightgreen)](tests/)

Bandeau cookies moderne, configurable depuis l'**admin Django**, sécurisé par **HMAC-SHA256**, conforme **RGPD/CNIL**, avec **72 intégrations tierces** et un tableau de bord `/cookiekit/` intégré.

</div>

---

## Fonctionnalités

- **Bandeau + modal préférences** — UI moderne 100 % CSS custom properties, sans dépendance JS
- **Configurable depuis l'admin Django** — zéro code côté settings pour tout sauf `enabled`
- **RGPD/CNIL** — analytics opt-in uniquement, durée max 395 jours (13 mois) respectée
- **HMAC-SHA256** — cookie signé côté serveur, cookie HttpOnly anti-falsification
- **72 intégrations** — Analytics, Session replay, Marketing pixels, Chat, CDP, A/B testing, Push notifications, Email tracking et plus
- **API JavaScript** — `hasConsent()`, `acceptAll()`, `rejectAll()`, événement `xeolux:cookies:updated`
- **Versioning du consentement** — le bandeau réapparaît si la version change
- **Compatibilité xeolux-cachekit** — cache-busting statiques + cookies versionnés, synchronisation de la version de consentement via `get_cache_version("cookies")`
- **Bridge xeolux-analyticskit** — prêt pour intégration future (package séparé)

---

## Sommaire

1. [Installation](#installation)
2. [Configuration rapide](#configuration-rapide)
3. [Intégration dans les templates](#intégration-dans-les-templates)
4. [Administration Django](#administration-django)
5. [Tableau de bord /cookiekit/](#tableau-de-bord-cookiekit)
6. [Intégrations tierces](#intégrations-tierces)
7. [Scripts personnalisés](#scripts-personnalisés)
8. [API JavaScript](#api-javascript)
9. [Personnalisation CSS](#personnalisation-css)
10. [Sécurité cookie HMAC](#sécurité-cookie-hmac)
11. [Catégories de cookies](#catégories-de-cookies)
12. [Versioning du consentement](#versioning-du-consentement)
13. [Compatibilité xeolux-cachekit](#compatibilité-xeolux-cachekit)
14. [Tests](#tests)
15. [Avertissement RGPD/CNIL](#avertissement-rgpdcnil)

---

## Installation

```bash
pip install xeolux-cookiekit
```

Avec support `xeolux-cachekit` :

```bash
pip install "xeolux-cookiekit[cachekit]"
```

### 1. Ajouter l'application

```python
# settings.py
INSTALLED_APPS = [
    ...
    "xeolux_cookiekit",
]
```

### 2. Déclarer les URLs *(recommandé)*

Ajoutez dans votre fichier `urls.py` principal pour activer la page `/cookiekit/` :

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("", include("xeolux_cookiekit.urls")),
]
```

### 3. Appliquer les migrations

```bash
python manage.py migrate xeolux_cookiekit
```

### 4. Activer le context processor *(recommandé)*

```python
# settings.py
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                ...
                "xeolux_cookiekit.context_processors.cookiekit_config",
            ],
        },
    },
]
```

---

## Configuration rapide

Dans `settings.py`, une seule ligne suffit :

```python
XEOLUX_COOKIEKIT = {"enabled": True}
```

> Tout le reste (style, textes, intégrations, catégories…) se configure dans l'**admin Django**.

---

## Intégration dans les templates

Dans votre `base.html` :

```html
{% load cookiekit_tags %}
<!DOCTYPE html>
<html>
<head>
    ...
    {% cookiekit_head %}
</head>
<body>
    {% cookiekit_body %}

    ...votre contenu...

    {% cookiekit_banner %}
</body>
</html>
```

### Script conditionnel par catégorie

```html
{% load cookiekit_tags %}

{% cookiekit_script "analytics" %}
<script>
    /* Ce bloc ne s'exécute que si "analytics" est consenti */
    myAnalyticsTool.init();
</script>
{% endcookiekit_script %}
```

---

## Administration Django

Accédez à `/admin/xeolux_cookiekit/cookiekitconfig/` pour tout configurer visuellement.

| Section admin | Contenu |
|---|---|
| **Général** | Activation, version de consentement, durée cookie |
| **🔒 Sécurité du cookie** | Signature HMAC-SHA256 (activée par défaut) |
| **Apparence** | Couleurs, position, layout, ombres, police |
| **Textes** | Labels des boutons, titres, lien politique de confidentialité |
| **Intégrations tierces** | Lien vers la gestion des 71 intégrations |
| **Scripts personnalisés** | HTML/JS `<head>` et `<body>` après consentement |
| **CacheKit / Versioning** | Synchronisation avec xeolux-cachekit |
| **AnalyticsKit** | Bridge vers xeolux-analyticskit (futur) |
| **Avancé** | CSS personnalisé, z-index |

### Actions rapides sur les intégrations

Depuis **Admin → Intégrations**, sélectionnez plusieurs intégrations et utilisez le menu **Actions** :

- **✅ Activer les intégrations sélectionnées** — active en masse
- **❌ Désactiver les intégrations sélectionnées** — désactive en masse

> ⚠️ L'ajout et la suppression d'intégrations sont intentionnellement bloqués. Seule la configuration (activation/désactivation + JSON) est modifiable.

### Priorité de configuration

| `config_source` | Comportement |
|---|---|
| `admin_fallback_settings` *(défaut)* | Admin en priorité, fallback sur settings.py |
| `settings_only` | Ignore l'admin — tout depuis settings.py |
| `admin_only` | Admin obligatoire — erreur si absent |

---

## Tableau de bord /cookiekit/

xeolux-cookiekit expose une page de tableau de bord simple, accessible aux membres autorisés de votre équipe **sans accès complet à l'admin Django**.

### Accès

| Condition | Comportement |
|---|---|
| Non connecté | Redirigé vers `/admin/login/` |
| Connecté sans permission | `403 Forbidden` |
| Connecté avec permission | Tableau de bord complet |

> **Important :** Le superuser n'a PAS accès automatiquement. La permission doit être attribuée explicitement (comportement voulu).

### Attribuer la permission

Dans **Admin → Utilisateurs**, cochez :
> `xeolux_cookiekit | Configuration CookieKit | Can view configuration cookiekit`

Ou par groupe — créez un groupe `CookieKit Editors` avec cette permission et assignez vos utilisateurs.

### Contenu du tableau de bord

- Statistiques : intégrations actives, total intégrations, catégories, version de consentement
- Carte **Configuration** : état, durée, cookie secure, signature HMAC
- Carte **CacheKit** : statut d'installation, version résolue, clé utilisée
- Carte **Catégories** : liste avec état activé/requis
- Grille **Intégrations** : toutes les intégrations groupées par catégorie avec badge actif/inactif

---

## Intégrations tierces

Les intégrations sont gérées via le modèle **`CookieKitIntegration`** (Admin → Intégrations). Chaque script est injecté **uniquement après consentement** à la catégorie correspondante. Aucune migration DB nécessaire pour ajouter une intégration.

### Analytics & statistiques web

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Google Analytics 4** | `analytics` | `measurement_id` |
| **Google Tag Manager** | `analytics` | `container_id` |
| **Matomo** | `analytics` | `site_id`, `tracker_url` |
| **Plausible Analytics** | `analytics` | `domain`, `script_url` |
| **Microsoft Clarity** | `analytics` | `project_id` |
| **Hotjar** | `analytics` | `site_id` |
| **Umami Analytics** | `analytics` | `website_id`, `script_url` |
| **Fathom Analytics** | `analytics` | `site_id` |
| **Cloudflare Web Analytics** | `analytics` | `token` |
| **HubSpot Tracking** | `analytics` | `portal_id` |
| **Simple Analytics** | `analytics` | `hostname` *(optionnel)* |
| **Clicky** | `analytics` | `site_id` |
| **StatCounter** | `analytics` | `project`, `security` |
| **Woopra** | `analytics` | `domain` |
| **Countly** | `analytics` | `app_key`, `server_url` |
| **Adobe Analytics** | `analytics` | `script_url` |
| **Piwik PRO** | `analytics` | `container_id`, `container_url` |
| **Visitors.now** | `analytics` | `token` |

### Product analytics / session replay

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Mixpanel** | `analytics` | `project_token` |
| **Amplitude** | `analytics` | `api_key` |
| **PostHog** | `analytics` | `api_key`, `host` |
| **Segment** | `analytics` | `write_key` |
| **Heap Analytics** | `analytics` | `app_id` |
| **FullStory** | `analytics` | `org_id` |
| **Smartlook** | `analytics` | `project_key` |
| **Mouseflow** | `analytics` | `website_id` |
| **Crazy Egg** | `analytics` | `account_number` |
| **Lucky Orange** | `analytics` | `site_id` |
| **LogRocket** | `analytics` | `app_id` |
| **Pendo** | `analytics` | `api_key` |
| **Kissmetrics** | `analytics` | `api_key` |
| **OpenReplay** | `analytics` | `project_key`, `ingest_point` |
| **Inspectlet** | `analytics` | `wid` |

### CDP / Data routing

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **RudderStack** | `analytics` | `write_key`, `data_plane_url` |
| **Snowplow** | `analytics` | `collector_url`, `app_id` |

### A/B testing

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Optimizely Web** | `analytics` | `project_id` |
| **VWO** | `analytics` | `account_id` |
| **AB Tasty** | `analytics` | `account_id` |
| **GrowthBook** | `analytics` | `client_key`, `api_host` |

### Marketing & publicité

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Meta Pixel** | `marketing` | `pixel_id` |
| **LinkedIn Insight Tag** | `marketing` | `partner_id` |
| **TikTok Pixel** | `marketing` | `pixel_id` |
| **Twitter / X Pixel** | `marketing` | `pixel_id` |
| **Pinterest Tag** | `marketing` | `tag_id` |
| **Snapchat Pixel** | `marketing` | `pixel_id` |
| **Reddit Pixel** | `marketing` | `advertiser_id` |
| **Quora Pixel** | `marketing` | `pixel_id` |
| **Brevo Tracker** | `marketing` | `client_key` |
| **Google Ads Conversion** | `marketing` | `conversion_id`, `conversion_label` |
| **Microsoft Advertising UET** | `marketing` | `tag_id` |
| **Criteo OneTag** | `marketing` | `account_id` |
| **AdRoll Pixel** | `marketing` | `adroll_adv_id`, `adroll_pix_id` |
| **The Trade Desk** | `marketing` | `advertiser_id` |
| **Taboola Pixel** | `marketing` | `account_id` |
| **Outbrain Pixel** | `marketing` | `account_id` |
| **Amazon Ads Insight Tag** | `marketing` | `advertiser_id` |
| **Klaviyo** | `marketing` | `public_api_key` |
| **Mailchimp Web Tracking** | `marketing` | `u`, `id` |
| **ActiveCampaign Site Tracking** | `marketing` | `account_id`, `tracking_url` |
| **Customer.io Tracking** | `marketing` | `site_id` |

### Support / Chat & push

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Crisp Chat** | `preferences` | `website_id` |
| **Intercom** | `preferences` | `app_id` |
| **Zendesk Chat** | `preferences` | `key` |
| **Tidio Chat** | `preferences` | `public_key` |
| **Freshchat** | `preferences` | `token`, `host` |
| **LiveChat** | `preferences` | `license` |
| **Drift** | `preferences` | `embed_id` |
| **tawk.to** | `preferences` | `property_id` |
| **Smartsupp** | `preferences` | `key` |
| **Olark** | `preferences` | `site_id` |
| **OneSignal** | `preferences` | `app_id` |
| **PushEngage** | `preferences` | `api_key` |

### Activation depuis l'admin

1. Allez dans **Admin → Xeolux CookieKit → Intégrations**
2. Sélectionnez une intégration (toutes sont créées automatiquement au premier `migrate`)
3. Cochez **Actif** et renseignez le champ **Configuration** (JSON) :
   ```json
   {"measurement_id": "G-XXXXXXXXXX"}
   ```
4. Sauvegardez — le script est actif immédiatement

> **Mise à jour du package :** Les configurations existantes (`enabled`, `config`) ne sont jamais écrasées lors d'un `pip install --upgrade`. Les nouvelles intégrations ajoutées au catalogue sont créées avec `enabled=False` et `config={}` par défaut.

---

## Scripts personnalisés

En plus des **72 intégrations tierces** (dont Visitors.now, Google Analytics, Meta Pixel…), vous pouvez ajouter vos propres scripts via **Admin → Scripts personnalisés**.

Chaque script est :
- associé à une **catégorie** (sélecteur dynamique basé sur vos `CookieCategory`)
- injecté en `<head>` ou `<body>` uniquement si la catégorie est consentie
- activable/désactivable individuellement

```html
<!-- Exemple : script injecté dans <head> si 'analytics' est consenti -->
<script>
  (function() {
    // Votre script personnalisé
    myTool.init("MY_KEY");
  })();
</script>
```

---

## API JavaScript

```javascript
// Vérifier le consentement d'une catégorie
window.XeoluxCookieKit.hasConsent("analytics"); // true | false

// Lire le consentement complet
window.XeoluxCookieKit.getConsent();
// { version: "1.0.0", updated_at: "...", choices: { necessary: true, analytics: true, ... } }

// Actions utilisateur
window.XeoluxCookieKit.acceptAll();
window.XeoluxCookieKit.rejectAll();
window.XeoluxCookieKit.savePreferences({ analytics: true, marketing: false });

// Interface
window.XeoluxCookieKit.openPreferences();
window.XeoluxCookieKit.closePreferences();
window.XeoluxCookieKit.resetConsent(); // Supprime le cookie, réaffiche le bandeau

// Écouter les changements de consentement
window.addEventListener("xeolux:cookies:updated", (event) => {
    const consent = event.detail;
    if (consent.choices.analytics) {
        // Activer vos outils analytics
    }
});
```

---

## Personnalisation CSS

Le style est piloté par des **CSS custom properties** (`--xck-*`) :

```css
:root {
    --xck-bg:             #111111;
    --xck-text:           #ffffff;
    --xck-primary:        #ff6b00;
    --xck-primary-text:   #ffffff;
    --xck-secondary:      #2b2b2b;
    --xck-secondary-text: #ffffff;
    --xck-radius:         14px;
    --xck-z-index:        9999;
    --xck-shadow:         0 8px 40px rgba(0,0,0,0.45);
    --xck-font:           system-ui, sans-serif;
}
```

Toutes les classes CSS sont préfixées `xck-` pour éviter les conflits :
`.xck-banner`, `.xck-modal`, `.xck-button`, `.xck-button--primary`, `.xck-toggle`, `.xck-category`…

Utilisez le champ **CSS personnalisé** dans l'admin pour tout surcharger.

---

## Sécurité cookie HMAC

xeolux-cookiekit implémente une stratégie **deux cookies** :

| Cookie | Accessible JS | Rôle |
|---|---|---|
| `xeolux_cookie_consent` | ✅ Oui | Stocke les choix (version, catégories) |
| `xeolux_cookie_consent_sig` | ❌ Non (HttpOnly) | Signature HMAC-SHA256 — détecte les falsifications |

La signature est calculée avec `settings.SECRET_KEY` + sel statique via `hmac.new(key, payload, sha256)`. Toute modification manuelle du cookie est détectée côté serveur.

**Vérification dans une view Django :**

```python
from xeolux_cookiekit.security import get_verified_consent

def my_view(request):
    consent = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
    if consent and consent.has("analytics"):
        # Consentement analytics vérifié et non falsifié
        ...
```

---

## Catégories de cookies

### Catégories intégrées

| Clé | Label | Requis | Défaut |
|---|---|---|---|
| `necessary` | Nécessaires | ✅ Oui | ✅ Toujours actif |
| `analytics` | Mesure d'audience | Non | ❌ Opt-in (CNIL) |
| `marketing` | Marketing | Non | ❌ Opt-in (CNIL) |
| `preferences` | Préférences | Non | ❌ Opt-in (CNIL) |

### Catégories personnalisées

Le modèle `CookieCategory` (admin) permet d'ajouter des catégories custom. Elles apparaissent automatiquement dans la modal de préférences.

```html
{% cookiekit_script "ma_categorie_custom" %}
<script>/* activé après consentement */</script>
{% endcookiekit_script %}
```

---

## Versioning du consentement

Si la `consent_version` change, le bandeau réapparaît pour tous les utilisateurs.

**Via l'admin :** champ `Version de consentement`, ou utilisez l'action **"Incrémenter la version (patch)"** depuis la liste.

---

## Compatibilité xeolux-cachekit

> 📦 [PyPI](https://pypi.org/project/xeolux-cachekit/) — [GitHub](https://github.com/Xeolux-Corp/Xeolux_cachekit)

`xeolux-cachekit` est un système de **cache-busting** Django pour fichiers statiques (CSS, JS, assets) et **cookies versionnés**. Il maintient des versions nommées pour chaque type de ressource, expose des URL versionnées (`/static/css/main.css?v=1.0.3`) et génère des noms de cookies incluant la version active.

```bash
pip install "xeolux-cookiekit[cachekit]"
```

### Principe d'intégration

Dans votre `settings.py`, configurez `XEOLUX_CACHEKIT` avec une clé `"cookies"` :

```python
XEOLUX_CACHEKIT = {
    "global": "1.0.0",
    "css": "1.0.3",
    "js": "1.2.0",
    "assets": "1.0.8",
    "cookies": "1.0.0",   # ← version lue par xeolux-cookiekit
    "strategy": "manual",  # ou "hash"
}
```

Lorsque `cachekit_enabled` et `cachekit_sync_cookie_version` sont activés dans l'admin, `xeolux-cookiekit` appelle `get_cache_version(kind)` pour récupérer la version de consentement dynamiquement, plutôt que de la gérer manuellement. Si la valeur de `"cookies"` change, le bandeau de consentement réapparaît automatiquement.

### Configuration dans l'admin

| Champ | Description |
|---|---|
| `cachekit_enabled` | Active l'intégration xeolux-cachekit |
| `cachekit_sync_cookie_version` | Synchronise la version de consentement via CacheKit |
| `cachekit_version_key` | Kind passé à `get_cache_version()` (défaut : `cookies`) |

### Fonctionnement sans xeolux-cachekit

Si le package n'est pas installé, `xeolux-cookiekit` fonctionne en mode dégradé normal — la version de consentement est gérée manuellement via le champ `consent_version` de l'admin.

---

## Tests

```bash
pip install "xeolux-cookiekit[dev]"
pytest
```

66 tests couvrent : config merge, RGPD/CNIL compliance, singleton admin, HMAC signing, payload validation, falsification detection, analytics bridge.

---

## Changelog

### v1.2.6 (2026)
- **Fix `admin.py`** — fieldsets Apparence réorganisés en 4 sections distinctes (Thème & Layout, Options avancées, Palette sombre, Palette claire) incluant tous les champs de v1.2.4

### v1.2.5 (2026)
- **Fix dashboard : suppression de la fusion ancien/nouveau template** — l'ancien code (v1.2.2) était collé après le nouveau dans `dashboard.html`, causant l'affichage de l'ancienne section Apparence et de l'ancienne sidebar
- **FontAwesome 6.5** — tous les emojis du dashboard remplacés par des icones FontAwesome (`fa-solid`) : sidebar, card headers, alertes, boutons, topbar
- **`saveConfig()` complété** — inclut maintenant tous les champs apparus en v1.2.4 (palettes light, options avancées bandeau)
- **Color pickers sync** — synchronisation bidirectionnelle étendue aux 14 champs couleur (dark + light + bordures)

### v1.2.4 (2026)
- **Palette dark/light configurable séparément** — 6 couleurs dark + 6 couleurs light + bordures, chacune éditable depuis le dashboard `/cookiekit/` ou l'admin. Fini le thème clair hardcodé Apple-style.
- **Plus de paramètres d'apparence** : largeur max (`banner_max_width`), taille du texte (`banner_font_size`), padding interne (`banner_padding`), border radius mobile, overlay sombre, couleur de bordure dark/light, z-index et police maintenant éditables depuis le dashboard
- **Nouvelles CSS custom properties** : `--xck-border`, `--xck-font-size`, `--xck-padding`, `--xck-max-width`, `--xck-radius-mobile`
- **Intégration Visitors.now** — 72ème intégration. Script `https://cdn.visitors.now/v.js` conditionné au consentement analytics. Config : `token`
- **Fix dashboard CacheKit** : la "Version consentement" dans la vue d'ensemble affiche désormais la version résolue par CacheKit (si sync active) et non la valeur brute de la DB. Indicateur ⚡ via CacheKit ajouté.

### v1.2.3 (2026)
- **Dashboard `/cookiekit/` entièrement réécrit** — sidebar de navigation, édition inline de toute la config (général, apparence, textes, intégrations, catégories, scripts custom)
- **CRUD scripts personnalisés** — création/modification/suppression via modal dans le dashboard (sans passer par l'admin)
- **Fix `conf.py`** : `get_cachekit_version()` utilise maintenant `get_cache_version` (corrigé + `version_key` default `"cookiekit"` → `"cookies"`)
- **Filtre template `get_item`** ajouté pour accès dict par clé dans les templates

### v1.2.2 (2026)
- **Dark / Light / Auto mode sur le bandeau** — le champ `banner_color_scheme` (`dark`/`light`/`auto`) pilote les CSS custom properties du bandeau de consentement et de la modal de préférences
  - `dark` : couleurs personnalisées via l'admin
  - `light` : thème clair prédéfini (Apple-style `#f5f5f7` / `#1d1d1f`)
  - `auto` : suit `prefers-color-scheme` système (dark par défaut, bascule clair si OS en mode clair)
- Attribut `data-xck-scheme` ajouté sur `#xck-banner` et `#xck-modal`
- Nouveaux champs `banner_animation` (slide/fade/none) et `banner_backdrop_blur` passés dans le dict `style`

### v1.2.1 (2026)
- **Fix critique CacheKit** : `cachekit_version_key` avait `default="cookiekit"` (invalide) — corrigé en `default="cookies"` + migration data `RunPython` pour mettre à jour les lignes DB existantes
- **Dashboard dark/light/auto mode** : toggle ☀/🌙/⚡ dans la topbar, CSS variables par thème, mémorisé en `localStorage`
- **Nouveaux champs apparence** : `banner_color_scheme`, `dashboard_theme`, `banner_animation`, `banner_backdrop_blur`
- **Carte Apparence** dans le dashboard : thème, animation, backdrop blur, palette de couleurs avec swatches

### v1.2.0 (2026)
- **71 intégrations** (+41 nouvelles) : Simple Analytics, Clicky, StatCounter, Woopra, Countly, Adobe Analytics, Piwik PRO, Smartlook, Mouseflow, Crazy Egg, Lucky Orange, LogRocket, Pendo, Kissmetrics, OpenReplay, Inspectlet, Google Ads Conversion, Microsoft UET, Criteo OneTag, AdRoll, The Trade Desk, Taboola, Outbrain, Amazon Ads, Klaviyo, Mailchimp Tracking, ActiveCampaign, Customer.io, LiveChat, Drift, tawk.to, Smartsupp, Olark, RudderStack, Snowplow, Optimizely, VWO, AB Tasty, GrowthBook, OneSignal, PushEngage
- Couvre désormais : analytics web, product analytics, session replay/heatmaps, marketing pixels, CDPs, A/B testing, push notifications, email marketing tracking, chat

### v1.1.5 (2026)
- **Fix intégration xeolux-cachekit** : corrige l'appel API (`get_cache_version()` à la place de l'ancienne `get_version()`) dans `views.py` et `admin.py`
- **README** : description complète de xeolux-cachekit (cache-busting CSS/JS/assets + cookies versionnés) et de son intégration via la clé `"cookies"`

### v1.1.4 (2026)
- **Dashboard `/cookiekit/` configurable** : UI Apple white mode, actions JSON (save_config, toggle_integration, save_intg_config, toggle_category)
- **`get_config_fields()`** sur `CookieKitIntegration` : champs de configuration structurés pour le template

### v1.1.3 (2026)
- **Sélecteur dynamique** pour le champ « Catégorie de consentement requise » dans l'admin des Scripts personnalisés — affiche les catégories existantes en base plutôt qu'un champ texte libre

### v1.1.2 (2026)
- **Nouveau tableau de bord `/cookiekit/`** — login requis + permission `view_cookiekitconfig` (pas de bypass superuser)
- **Actions admin** sur les intégrations : activer/désactiver en masse
- **Intégrations** : ajout et suppression interdits via l'admin (configuration uniquement)
- **`slug` en lecture seule** dans le formulaire intégration
- **Fix détection CacheKit** : `importlib.util.find_spec` distingue « non installé » de « installé mais `get_version()` manquant »

### v1.1.1 (2026)
- Correction doublon `@admin.register` dans `admin.py` (erreur `AlreadyRegistered`)

### v1.1.0 (2025)
- **Nouveau modèle `CookieKitIntegration`** — remplace les 22 champs individuels d'intégration de `CookieKitConfig` par un modèle générique avec `JSONField`
- **71 intégrations** (+41 nouvelles) : Mixpanel, Amplitude, PostHog, Umami, Fathom, Segment, Heap, FullStory, Cloudflare Web Analytics, HubSpot, Pinterest Tag, Snapchat Pixel, Reddit Pixel, Quora Pixel, Brevo, Intercom, Zendesk Chat, Tidio, Freshchat, et plus
- **Nouveau fichier `integrations.py`** — catalogue centralisé + générateurs JS individuels
- Ajout d'un admin `CookieKitIntegrationAdmin` avec aide contextuelle JSON
- Auto-création des 30 intégrations au `migrate` (toutes désactivées par défaut)
- Migrations 0007 (création table) + 0008 (suppression anciens champs)

### v1.0.1 (2025)
- Correctif `banner.html` (balise `<button>` manquante — texte "Refuser" affiché en clair)
- Catégories auto-créées via signal `post_migrate`
- Champ `cachekit_version_status` dans l'admin
- Suppression des champs redondants `custom_head/body_scripts`

### v1.0.0 (2025)
- Version initiale : bandeau RGPD, modal préférences, 11 intégrations, HMAC-SHA256, CacheKit bridge

---

## Avertissement RGPD/CNIL

> **Ce package est un outil technique. Il ne constitue pas un conseil juridique.**
>
> La conformité RGPD/CNIL dépend de votre implémentation, de votre politique de confidentialité et de la nature de vos traitements. Consultez la [documentation CNIL](https://www.cnil.fr/fr/cookies-et-autres-traceurs) et un juriste pour votre conformité.

---

<div align="center">

**© 2026 [Xeolux](https://github.com/Xeolux-Corp)** — Licence MIT

</div>