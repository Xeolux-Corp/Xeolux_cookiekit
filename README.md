<div align="center">

# 🍪 xeolux-cookiekit

**Package Django de gestion du consentement cookies — RGPD/CNIL ready**

[![PyPI version](https://img.shields.io/pypi/v/xeolux-cookiekit.svg?color=ff6b00)](https://pypi.org/project/xeolux-cookiekit/)
[![Python](https://img.shields.io/pypi/pyversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![Django](https://img.shields.io/pypi/djversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-66%20passed-brightgreen)](tests/)

Bandeau cookies moderne, configurable depuis l'**admin Django**, sécurisé par **HMAC-SHA256**, conforme **RGPD/CNIL**, avec **30 intégrations tierces** et un tableau de bord `/cookiekit/` intégré.

</div>

---

## Fonctionnalités

- **Bandeau + modal préférences** — UI moderne 100 % CSS custom properties, sans dépendance JS
- **Configurable depuis l'admin Django** — zéro code côté settings pour tout sauf `enabled`
- **RGPD/CNIL** — analytics opt-in uniquement, durée max 395 jours (13 mois) respectée
- **HMAC-SHA256** — cookie signé côté serveur, cookie HttpOnly anti-falsification
- **30 intégrations** — GA4, GTM, Meta Pixel, LinkedIn, TikTok, X/Twitter, Matomo, Plausible, Clarity, Hotjar, Crisp, Mixpanel, Amplitude, PostHog, Intercom, Zendesk, et plus
- **API JavaScript** — `hasConsent()`, `acceptAll()`, `rejectAll()`, événement `xeolux:cookies:updated`
- **Versioning du consentement** — le bandeau réapparaît si la version change
- **Compatibilité xeolux-cachekit** — synchronisation de version optionnelle
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
| **Intégrations tierces** | Lien vers la gestion des 30 intégrations |
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

### Analytics

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Google Analytics 4** | `analytics` | `measurement_id` |
| **Google Tag Manager** | `analytics` | `container_id` |
| **Matomo** | `analytics` | `site_id`, `tracker_url` |
| **Plausible Analytics** | `analytics` | `domain`, `script_url` |
| **Microsoft Clarity** | `analytics` | `project_id` |
| **Hotjar** | `analytics` | `site_id` |
| **Mixpanel** | `analytics` | `project_token` |
| **Amplitude** | `analytics` | `api_key` |
| **PostHog** | `analytics` | `api_key`, `host` |
| **Umami Analytics** | `analytics` | `website_id`, `script_url` |
| **Fathom Analytics** | `analytics` | `site_id` |
| **Segment** | `analytics` | `write_key` |
| **Heap Analytics** | `analytics` | `app_id` |
| **FullStory** | `analytics` | `org_id` |
| **Cloudflare Web Analytics** | `analytics` | `token` |
| **HubSpot Tracking** | `analytics` | `portal_id` |

### Marketing

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

### Support / Chat

| Intégration | Catégorie | Config JSON |
|---|---|---|
| **Crisp Chat** | `preferences` | `website_id` |
| **Intercom** | `preferences` | `app_id` |
| **Zendesk Chat** | `preferences` | `key` |
| **Tidio Chat** | `preferences` | `public_key` |
| **Freshchat** | `preferences` | `token`, `host` |

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

En plus des 30 intégrations tierces, vous pouvez ajouter vos propres scripts via **Admin → Scripts personnalisés**.

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

```bash
pip install "xeolux-cookiekit[cachekit]"
```

Si `xeolux_cachekit` est installé et que `cachekit.sync_cookie_version` est activé, la version de consentement est synchronisée avec la version cachekit. Fonctionne en mode dégradé sans cachekit.

---

## Tests

```bash
pip install "xeolux-cookiekit[dev]"
pytest
```

66 tests couvrent : config merge, RGPD/CNIL compliance, singleton admin, HMAC signing, payload validation, falsification detection, analytics bridge.

---

## Changelog

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
- **30 intégrations** (15 nouvelles) : Mixpanel, Amplitude, PostHog, Umami, Fathom, Segment, Heap, FullStory, Cloudflare Web Analytics, HubSpot, Pinterest Tag, Snapchat Pixel, Reddit Pixel, Quora Pixel, Brevo, Intercom, Zendesk Chat, Tidio, Freshchat
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