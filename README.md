<div align="center">

# 🍪 xeolux-cookiekit

**Package Django de gestion du consentement cookies — RGPD/CNIL ready**

[![PyPI version](https://img.shields.io/pypi/v/xeolux-cookiekit.svg?color=ff6b00)](https://pypi.org/project/xeolux-cookiekit/)
[![Python](https://img.shields.io/pypi/pyversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![Django](https://img.shields.io/pypi/djversions/xeolux-cookiekit.svg)](https://pypi.org/project/xeolux-cookiekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-66%20passed-brightgreen)](tests/)

Bandeau cookies moderne, configurable depuis l'**admin Django**, sécurisé par **HMAC-SHA256**, conforme **RGPD/CNIL**, avec 11 intégrations tierces prêtes à l'emploi.

</div>

---

## Fonctionnalités

- **Bandeau + modal préférences** — UI moderne 100 % CSS custom properties, sans dépendance JS
- **Configurable depuis l'admin Django** — zéro code côté settings pour tout sauf `enabled`
- **RGPD/CNIL** — analytics opt-in uniquement, durée max 395 jours (13 mois) respectée
- **HMAC-SHA256** — cookie signé côté serveur, cookie HttpOnly anti-falsification
- **11 intégrations** — GA4, GTM, Meta Pixel, LinkedIn, TikTok, X/Twitter, Matomo, Plausible, Clarity, Hotjar, Crisp
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
5. [Intégrations tierces](#intégrations-tierces)
6. [API JavaScript](#api-javascript)
7. [Personnalisation CSS](#personnalisation-css)
8. [Sécurité cookie HMAC](#sécurité-cookie-hmac)
9. [Catégories de cookies](#catégories-de-cookies)
10. [Versioning du consentement](#versioning-du-consentement)
11. [Compatibilité xeolux-cachekit](#compatibilité-xeolux-cachekit)
12. [Tests](#tests)
13. [Avertissement RGPD/CNIL](#avertissement-rgpdcnil)

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

### 2. Appliquer les migrations

```bash
python manage.py migrate xeolux_cookiekit
```

### 3. Activer le context processor *(recommandé)*

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
| **Intégrations Google** | GA4 (G-xxx), GTM (GTM-xxx) |
| **Autres intégrations** | Meta, LinkedIn, TikTok, Twitter/X, Matomo, Plausible, Clarity, Hotjar, Crisp |
| **Scripts personnalisés** | HTML/JS `<head>` et `<body>` après consentement |
| **CacheKit / Versioning** | Synchronisation avec xeolux-cachekit |
| **AnalyticsKit** | Bridge vers xeolux-analyticskit (futur) |
| **Avancé** | CSS personnalisé, z-index |

### Priorité de configuration

| `config_source` | Comportement |
|---|---|
| `admin_fallback_settings` *(défaut)* | Admin en priorité, fallback sur settings.py |
| `settings_only` | Ignore l'admin — tout depuis settings.py |
| `admin_only` | Admin obligatoire — erreur si absent |

---

## Intégrations tierces

Toutes les intégrations s'activent depuis l'**admin Django**. Chaque script est injecté **uniquement après consentement** à la catégorie correspondante.

### Analytiques

| Intégration | Catégorie | Champ admin |
|---|---|---|
| **Google Analytics 4** | `analytics` | Measurement ID (`G-XXXXXXXXXX`) |
| **Google Tag Manager** | `analytics` | Container ID (`GTM-XXXXXXX`) |
| **Matomo** | `analytics` | Site ID + Tracker URL |
| **Plausible** | `analytics` | Domain |
| **Microsoft Clarity** | `analytics` | Project ID |
| **Hotjar** | `analytics` | Site ID |

### Marketing

| Intégration | Catégorie | Champ admin |
|---|---|---|
| **Meta Pixel** | `marketing` | Pixel ID |
| **LinkedIn Insight Tag** | `marketing` | Partner ID |
| **TikTok Pixel** | `marketing` | Pixel ID |
| **Twitter / X Pixel** | `marketing` | Pixel ID |

### Préférences

| Intégration | Catégorie | Champ admin |
|---|---|---|
| **Crisp Chat** | `preferences` | Website ID (UUID) |

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

## Avertissement RGPD/CNIL

> **Ce package est un outil technique. Il ne constitue pas un conseil juridique.**
>
> La conformité RGPD/CNIL dépend de votre implémentation, de votre politique de confidentialité et de la nature de vos traitements. Consultez la [documentation CNIL](https://www.cnil.fr/fr/cookies-et-autres-traceurs) et un juriste pour votre conformité.

---

<div align="center">

**© 2026 [Xeolux](https://github.com/Xeolux-Corp)** — Licence MIT

</div>
