/**
 * xeolux_cookiekit — cookiekit.js
 * Gestion du consentement cookies en vanilla JS.
 *
 * API publique exposée sur window.XeoluxCookieKit :
 *   init(config)
 *   acceptAll()
 *   rejectAll()
 *   savePreferences(choices)
 *   hasConsent(category)
 *   getConsent()
 *   openPreferences()
 *   closePreferences()
 *   resetConsent()
 *
 * Événement dispatché à chaque changement :
 *   window.dispatchEvent(new CustomEvent("xeolux:cookies:updated", { detail: consent }))
 */

(function () {
  "use strict";

  // ── Config interne ──────────────────────────────────────────────────────────
  var _config = {};
  var _initialized = false;

  // ── Constantes de sécurité ──────────────────────────────────────────────────
  var _SECURITY = {
    MAX_PAYLOAD_BYTES: 2048,      // Taille max du cookie en caractères
    MAX_CATEGORIES: 20,           // Nombre max de catégories dans choices
    MAX_VERSION_LEN: 20,          // Longueur max de la version
    MAX_CATEGORY_KEY_LEN: 50,     // Longueur max d'une clé de catégorie
    CATEGORY_KEY_RE: /^[a-z0-9_\-]{1,50}$/,  // Slug valide
    VERSION_RE: /^[\d.a-zA-Z\-]{1,20}$/,     // Version sémantique
  };

  // ── Éléments DOM (référencés après DOMContentLoaded) ───────────────────────
  var _banner = null;
  var _modal = null;
  var _backdrop = null;

  // ── Focus trap pour l'accessibilité ────────────────────────────────────────
  var _lastFocusBeforeModal = null;

  // ══════════════════════════════════════════════════════════════════════════
  //  Cookie helpers
  // ══════════════════════════════════════════════════════════════════════════

  function _setCookie(name, value, maxAge, secure, sameSite) {
    // Validation du nom du cookie (RFC 6265 — pas de caractères de contrôle)
    if (!/^[a-zA-Z0-9_\-]+$/.test(name)) {
      console.error("[XeoluxCookieKit] Nom de cookie invalide :", name);
      return;
    }
    var cookieStr =
      encodeURIComponent(name) + "=" + encodeURIComponent(value) +
      "; max-age=" + Math.min(parseInt(maxAge, 10) || 0, 34128000) + // max ~395j
      "; path=/" +
      "; SameSite=" + (sameSite || "Lax");
    if (secure && location.protocol === "https:") {
      cookieStr += "; Secure";
    }
    document.cookie = cookieStr;
  }

  function _getCookie(name) {
    // Validation du nom avant recherche
    if (!/^[a-zA-Z0-9_\-]+$/.test(name)) return null;
    var encodedName = encodeURIComponent(name);
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.indexOf(encodedName + "=") === 0) {
        try {
          var raw = decodeURIComponent(cookie.substring(encodedName.length + 1));
          // Limite de taille : cookie suspect si > MAX_PAYLOAD_BYTES
          if (raw.length > _SECURITY.MAX_PAYLOAD_BYTES) {
            _log("warn", "Cookie trop large (" + raw.length + " chars) — rejeté.");
            return null;
          }
          return raw;
        } catch (e) {
          return null;
        }
      }
    }
    return null;
  }

  function _deleteCookie(name) {
    if (!/^[a-zA-Z0-9_\-]+$/.test(name)) return;
    document.cookie =
      encodeURIComponent(name) +
      "=; max-age=0; path=/; SameSite=Lax";
  }

  function _log(level, msg) {
    if (_config.debug) {
      if (level === "warn") console.warn("[XeoluxCookieKit]", msg);
      else console.log("[XeoluxCookieKit]", msg);
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Consentement — lecture / écriture sécurisées
  // ══════════════════════════════════════════════════════════════════════════

  /**
   * Valide et assainit le payload de consentement.
   * - Whitelist des clés de catégories (slug a-z0-9_-)
   * - Valeurs uniquement booléennes
   * - Version au format attendu
   * - Nombre de catégories limité
   * Retourne un objet propre ou null si invalide.
   */
  function _sanitizeConsent(data) {
    if (!data || typeof data !== "object" || Array.isArray(data)) return null;

    // Version
    var version = data.version;
    if (
      typeof version !== "string" ||
      !_SECURITY.VERSION_RE.test(version)
    ) {
      _log("warn", "Version de consentement invalide : " + JSON.stringify(version));
      return null;
    }

    // Choices
    var choices = data.choices;
    if (!choices || typeof choices !== "object" || Array.isArray(choices)) {
      _log("warn", "Champ 'choices' invalide.");
      return null;
    }

    var keys = Object.keys(choices);
    if (keys.length > _SECURITY.MAX_CATEGORIES) {
      _log("warn", "Trop de catégories dans le cookie (" + keys.length + ").");
      return null;
    }

    // Assainir les choices : clés whitelistées + valeurs booléennes uniquement
    var cleanChoices = {};
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      // Clé doit être un slug valide
      if (
        typeof key !== "string" ||
        !_SECURITY.CATEGORY_KEY_RE.test(key)
      ) {
        _log("warn", "Clé de catégorie ignorée (invalide) : " + JSON.stringify(key));
        continue;
      }
      cleanChoices[key] = choices[key] === true; // Strict boolean cast
    }

    // necessary est toujours true (défense en profondeur)
    cleanChoices["necessary"] = true;

    return {
      version: version,
      updated_at: (typeof data.updated_at === "string" && data.updated_at.length <= 30)
        ? data.updated_at
        : "",
      choices: cleanChoices,
    };
  }

  function _readConsent() {
    var raw = _getCookie(_config.cookie_name || "xeolux_cookie_consent");
    if (!raw) return null;
    try {
      var parsed = JSON.parse(raw);
      return _sanitizeConsent(parsed);
    } catch (e) {
      _log("warn", "Cookie de consentement JSON invalide — rejeté.");
      return null;
    }
  }

  function _writeConsent(choices) {
    // Assainir les choices avant écriture
    var cleanChoices = {};
    var cats = _config.categories || {};

    // Partir des catégories connues de la config pour éviter toute injection
    Object.keys(cats).forEach(function (key) {
      if (_SECURITY.CATEGORY_KEY_RE.test(key)) {
        if (cats[key].required) {
          cleanChoices[key] = true; // Requis = toujours true
        } else {
          cleanChoices[key] = choices[key] === true;
        }
      }
    });
    // necessary toujours true
    cleanChoices["necessary"] = true;

    var consent = {
      version: _config.consent_version || "1.0.0",
      updated_at: new Date().toISOString(),
      choices: cleanChoices,
    };
    var json = JSON.stringify(consent);

    // Vérification de taille avant écriture
    if (json.length > _SECURITY.MAX_PAYLOAD_BYTES) {
      _log("warn", "Payload de consentement trop large — écriture annulée.");
      return consent;
    }

    _setCookie(
      _config.cookie_name || "xeolux_cookie_consent",
      json,
      _config.cookie_max_age || 15552000,
      _config.cookie_secure !== false,
      _config.cookie_samesite || "Lax"
    );
    return consent;
  }

  function _isConsentValid(consent) {
    if (!consent) return false;
    if (typeof consent.version !== "string") return false;
    if (consent.version !== (_config.consent_version || "1.0.0")) return false;
    if (!consent.choices || typeof consent.choices !== "object") return false;
    return true;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Activation des scripts encapsulés
  // ══════════════════════════════════════════════════════════════════════════

  /**
   * Active les scripts `<script type="text/plain" data-xck-category="X">`.
   * Pour chaque script dont la catégorie est consentie, on crée un nouveau
   * nœud <script> exécutable et on le remplace dans le DOM.
   */
  function _activatePendingScripts(consent) {
    var pendingScripts = document.querySelectorAll(
      'script[type="text/plain"][data-xck-script="1"]'
    );

    pendingScripts.forEach(function (el) {
      var category = el.getAttribute("data-xck-category");
      if (!category) return;
      if (!consent.choices[category]) return;
      if (el.getAttribute("data-xck-activated")) return;

      // Marquer comme activé avant de créer le nouveau nœud
      el.setAttribute("data-xck-activated", "1");

      var newScript = document.createElement("script");
      // Copier les attributs (sauf type et data-xck-*)
      Array.prototype.forEach.call(el.attributes, function (attr) {
        if (
          attr.name !== "type" &&
          attr.name !== "data-xck-script" &&
          attr.name !== "data-xck-activated"
        ) {
          newScript.setAttribute(attr.name, attr.value);
        }
      });
      newScript.textContent = el.textContent;
      el.parentNode.replaceChild(newScript, el);
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Dispatch de l'événement de consentement
  // ══════════════════════════════════════════════════════════════════════════

  function _dispatchConsentEvent(consent) {
    try {
      var event = new CustomEvent("xeolux:cookies:updated", {
        detail: consent,
        bubbles: false,
        cancelable: false,
      });
      window.dispatchEvent(event);
    } catch (e) {
      // Compatibilité IE (non requise mais défensive)
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Bandeau — affichage / masquage
  // ══════════════════════════════════════════════════════════════════════════

  function _showBanner() {
    if (!_banner) return;
    _banner.hidden = false;
    // Forcer un reflow pour déclencher la transition CSS
    void _banner.offsetWidth;
    _banner.classList.add("xck-visible");
    _banner.removeAttribute("aria-hidden");
    // Focus sur le premier bouton pour l'accessibilité
    var firstBtn = _banner.querySelector(".xck-button");
    if (firstBtn) setTimeout(function () { firstBtn.focus(); }, 50);
  }

  function _hideBanner() {
    if (!_banner) return;
    _banner.classList.remove("xck-visible");
    _banner.setAttribute("aria-hidden", "true");
    setTimeout(function () {
      if (_banner) _banner.hidden = true;
    }, 300);
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Modal préférences
  // ══════════════════════════════════════════════════════════════════════════

  function _openModal() {
    if (!_modal) return;
    _lastFocusBeforeModal = document.activeElement;
    _modal.hidden = false;
    void _modal.offsetWidth;
    _modal.classList.add("xck-visible");
    _modal.removeAttribute("aria-hidden");
    document.body.style.overflow = "hidden";
    // Synchroniser les toggles avec le consentement courant
    _syncTogglesToConsent();
    // Focus sur le premier toggle / bouton
    var firstFocusable = _modal.querySelector("button, input");
    if (firstFocusable) setTimeout(function () { firstFocusable.focus(); }, 60);
    // Annoncer aux lecteurs d'écran
    _banner && _banner.querySelector("#xck-btn-customize") &&
      _banner.querySelector("#xck-btn-customize").setAttribute("aria-expanded", "true");
  }

  function _closeModal() {
    if (!_modal) return;
    _modal.classList.remove("xck-visible");
    _modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    setTimeout(function () {
      if (_modal) _modal.hidden = true;
    }, 300);
    if (_lastFocusBeforeModal) {
      try { _lastFocusBeforeModal.focus(); } catch (e) {}
    }
    _banner && _banner.querySelector("#xck-btn-customize") &&
      _banner.querySelector("#xck-btn-customize").setAttribute("aria-expanded", "false");
  }

  function _syncTogglesToConsent() {
    var consent = _readConsent();
    var checkboxes = _modal
      ? _modal.querySelectorAll('input[type="checkbox"][data-category]')
      : [];
    checkboxes.forEach(function (cb) {
      var cat = cb.getAttribute("data-category");
      if (cb.disabled) return; // Requis — toujours coché
      if (consent && consent.choices && typeof consent.choices[cat] === "boolean") {
        cb.checked = consent.choices[cat];
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Construire les choices depuis les toggles de la modal
  // ══════════════════════════════════════════════════════════════════════════

  function _buildChoicesFromModal() {
    var choices = {};
    var cats = _config.categories || {};
    // Toujours activer les catégories requises
    Object.keys(cats).forEach(function (key) {
      choices[key] = cats[key].required ? true : false;
    });
    // Lire les toggles
    var checkboxes = _modal
      ? _modal.querySelectorAll('input[type="checkbox"][data-category]')
      : [];
    checkboxes.forEach(function (cb) {
      choices[cb.getAttribute("data-category")] = cb.checked;
    });
    // Les nécessaires sont toujours vrais
    choices.necessary = true;
    return choices;
  }

  function _buildAllChoices(value) {
    var choices = {};
    var cats = _config.categories || {};
    Object.keys(cats).forEach(function (key) {
      choices[key] = cats[key].required ? true : value;
    });
    choices.necessary = true;
    return choices;
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Enregistrement du consentement + effets
  // ══════════════════════════════════════════════════════════════════════════

  function _applyConsent(consent) {
    _activatePendingScripts(consent);
    _dispatchConsentEvent(consent);
    _hideBanner();
    _closeModal();
    _log("log", "Consentement enregistré : " + JSON.stringify(consent.choices));
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Trap focus dans la modal (accessibilité)
  // ══════════════════════════════════════════════════════════════════════════

  function _trapFocus(e) {
    if (!_modal || _modal.hidden) return;
    var focusable = _modal.querySelectorAll(
      'button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  Liaison des événements DOM
  // ══════════════════════════════════════════════════════════════════════════

  function _bindEvents() {
    // Bandeau
    var btnAccept = document.getElementById("xck-btn-accept");
    var btnReject = document.getElementById("xck-btn-reject");
    var btnCustomize = document.getElementById("xck-btn-customize");

    if (btnAccept) btnAccept.addEventListener("click", function () { XeoluxCookieKit.acceptAll(); });
    if (btnReject) btnReject.addEventListener("click", function () { XeoluxCookieKit.rejectAll(); });
    if (btnCustomize) btnCustomize.addEventListener("click", function () { XeoluxCookieKit.openPreferences(); });

    // Modal
    var modalClose = document.getElementById("xck-modal-close");
    var modalSave = document.getElementById("xck-modal-save");
    var modalReject = document.getElementById("xck-modal-reject");
    var modalBackdrop = document.getElementById("xck-modal-backdrop");

    if (modalClose) modalClose.addEventListener("click", function () { XeoluxCookieKit.closePreferences(); });
    if (modalSave) modalSave.addEventListener("click", function () {
      var choices = _buildChoicesFromModal();
      XeoluxCookieKit.savePreferences(choices);
    });
    if (modalReject) modalReject.addEventListener("click", function () { XeoluxCookieKit.rejectAll(); });
    if (modalBackdrop) modalBackdrop.addEventListener("click", function () { XeoluxCookieKit.closePreferences(); });

    // Touche Echap pour fermer la modal
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" || e.key === "Esc") {
        if (_modal && !_modal.hidden) {
          XeoluxCookieKit.closePreferences();
        }
      }
      if (e.key === "Tab") {
        _trapFocus(e);
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  //  API publique
  // ══════════════════════════════════════════════════════════════════════════

  var XeoluxCookieKit = {

    /**
     * Initialise CookieKit avec la configuration fournie.
     * Appelé automatiquement depuis window.__XCK_CONFIG__ si présent.
     */
    init: function (config) {
      if (_initialized) return;
      _initialized = true;
      _config = config || {};

      if (_config.debug) {
        console.log("[XeoluxCookieKit] Init avec :", _config);
      }

      _banner = document.getElementById("xck-banner");
      _modal = document.getElementById("xck-modal");
      _backdrop = document.getElementById("xck-modal-backdrop");

      _bindEvents();

      var consent = _readConsent();

      if (!_isConsentValid(consent)) {
        _showBanner();
        _log("log", "Aucun consentement valide — bandeau affiché.");
      } else {
        _activatePendingScripts(consent);
        _dispatchConsentEvent(consent);
        _log("log", "Consentement existant valide : " + consent.version);
      }
    },

    /** Accepte toutes les catégories. */
    acceptAll: function () {
      var choices = _buildAllChoices(true);
      var consent = _writeConsent(choices);
      _applyConsent(consent);
    },

    /** Refuse toutes les catégories optionnelles. */
    rejectAll: function () {
      var choices = _buildAllChoices(false);
      var consent = _writeConsent(choices);
      _applyConsent(consent);
    },

    /**
     * Enregistre des préférences personnalisées.
     * @param {Object} choices - Ex : { analytics: true, marketing: false }
     */
    savePreferences: function (choices) {
      // S'assurer que les nécessaires sont toujours vrais
      var finalChoices = Object.assign({}, choices);
      finalChoices.necessary = true;
      // Appliquer les requis depuis la config
      var cats = _config.categories || {};
      Object.keys(cats).forEach(function (key) {
        if (cats[key].required) finalChoices[key] = true;
      });
      var consent = _writeConsent(finalChoices);
      _applyConsent(consent);
    },

    /**
     * Vérifie si une catégorie est consentie.
     * @param {string} category
     * @returns {boolean}
     */
    hasConsent: function (category) {
      // Validation de la catégorie demandée (defence en profondeur)
      if (typeof category !== "string" || !_SECURITY.CATEGORY_KEY_RE.test(category)) {
        return false;
      }
      var consent = _readConsent();
      if (!consent || !_isConsentValid(consent)) return false;
      return consent.choices[category] === true;
    },

    /**
     * Retourne l'objet complet de consentement stocké.
     * @returns {Object|null}
     */
    getConsent: function () {
      return _readConsent();
    },

    /** Ouvre la modal de préférences. */
    openPreferences: function () {
      _openModal();
    },

    /** Ferme la modal de préférences. */
    closePreferences: function () {
      _closeModal();
    },

    /**
     * Réinitialise le consentement (supprime le cookie).
     * Force le réaffichage du bandeau au rechargement.
     */
    resetConsent: function () {
      _deleteCookie(_config.cookie_name || "xeolux_cookie_consent");
      _initialized = false;
      if (_banner) {
        _banner.hidden = false;
        void _banner.offsetWidth;
        _banner.classList.add("xck-visible");
        _banner.removeAttribute("aria-hidden");
      }
      _initialized = true;
      _log("log", "Consentement réinitialisé.");
    },
  };

  // ══════════════════════════════════════════════════════════════════════════
  //  Auto-init depuis window.__XCK_CONFIG__
  // ══════════════════════════════════════════════════════════════════════════

  function _autoInit() {
    if (window.__XCK_CONFIG__) {
      XeoluxCookieKit.init(window.__XCK_CONFIG__);
    } else if (window.XeoluxCookieKit && window.XeoluxCookieKit._pendingConfig) {
      XeoluxCookieKit.init(window.XeoluxCookieKit._pendingConfig);
    }
  }

  // Exposer l'API
  window.XeoluxCookieKit = XeoluxCookieKit;

  // Initialiser dès que le DOM est prêt
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _autoInit);
  } else {
    _autoInit();
  }
})();
