"""
analyticskit_bridge.py — Pont d'intégration entre xeolux_cookiekit et xeolux_analyticskit.

NOTE : xeolux-analyticskit est un package séparé, indépendant de cookiekit.
       Ce fichier définit l'interface contractuelle que analyticskit devra implémenter.
       Il fonctionne en mode dégradé si analyticskit n'est pas installé.

═══════════════════════════════════════════════════════════════
  xeolux-cookiekit    ──bridge──►    xeolux-analyticskit
  (ce package)                       (package futur séparé)
═══════════════════════════════════════════════════════════════

Contrat d'interface JS (stable, ne changera pas) :
──────────────────────────────────────────────────
  window.addEventListener("xeolux:cookies:updated", function(event) {
      var consent = event.detail;
      // consent = {
      //   version: "1.0.0",
      //   updated_at: "2026-04-27T12:00:00Z",
      //   choices: {
      //     necessary: true,
      //     analytics: true,   ← active/désactive les trackers analytics
      //     marketing: false,  ← active/désactive les pixels marketing
      //     preferences: false
      //   }
      // }
      // Analyticskit implémente cette écoute côté JS.
  });

Contrat d'interface Python (stable, ne changera pas) :
───────────────────────────────────────────────────────
  # analyticskit s'enregistre dans cookiekit au démarrage :
  from xeolux_cookiekit.analyticskit_bridge import register_analyticskit_handler

  def on_consent_updated(consent: dict) -> None:
      if consent["choices"].get("analytics"):
          my_analytics.enable()
      else:
          my_analytics.disable()

  register_analyticskit_handler(on_consent_updated)

  # Vérification depuis une view Django :
  from xeolux_cookiekit.analyticskit_bridge import get_bridge_status
  status = get_bridge_status()
  # → {"analyticskit_available": True, "handlers_count": 1, "handlers": ["on_consent_updated"]}
"""

from __future__ import annotations

import logging
from typing import Any, Callable

logger = logging.getLogger("xeolux_cookiekit.analyticskit")

# ── Registre des handlers analyticskit ────────────────────────────────────────
_analyticskit_handlers: list[Callable[[dict[str, Any]], None]] = []

# ── État de disponibilité analyticskit ────────────────────────────────────────
_analyticskit_available: bool | None = None  # None = non testé


def _check_analyticskit_available() -> bool:
    """
    Vérifie si xeolux_analyticskit est installé.
    Résultat mis en cache après le premier appel.
    """
    global _analyticskit_available
    if _analyticskit_available is None:
        try:
            import xeolux_analyticskit  # type: ignore[import]  # noqa: F401
            _analyticskit_available = True
            logger.debug("xeolux_analyticskit détecté — bridge activé.")
        except ImportError:
            _analyticskit_available = False
            logger.debug("xeolux_analyticskit non installé — bridge en mode dégradé.")
    return _analyticskit_available


def register_analyticskit_handler(handler: Callable[[dict[str, Any]], None]) -> None:
    """
    Enregistre un handler à appeler lors de chaque changement de consentement.

    Le handler reçoit un dict avec la structure suivante :
    {
        "version": "1.0.0",
        "updated_at": "2026-04-27T12:00:00Z",
        "choices": {
            "necessary": True,
            "analytics": True,
            "marketing": False,
            "preferences": False,
        }
    }

    Usage (depuis analyticskit) :
        from xeolux_cookiekit.analyticskit_bridge import register_analyticskit_handler

        def on_consent_updated(consent: dict) -> None:
            if consent["choices"].get("analytics"):
                my_analytics.enable()
            else:
                my_analytics.disable()

        register_analyticskit_handler(on_consent_updated)
    """
    if handler not in _analyticskit_handlers:
        _analyticskit_handlers.append(handler)
        logger.debug("Handler analyticskit enregistré : %s", handler.__name__)


def unregister_analyticskit_handler(handler: Callable[[dict[str, Any]], None]) -> None:
    """Désenregistre un handler précédemment enregistré."""
    try:
        _analyticskit_handlers.remove(handler)
    except ValueError:
        pass


def dispatch_consent_to_analyticskit(consent: dict[str, Any]) -> None:
    """
    Transmet un objet de consentement à tous les handlers enregistrés.

    Appelé depuis conf.py ou depuis un signal Django après sauvegarde du consentement.
    Les erreurs dans les handlers sont capturées pour ne pas bloquer le flux principal.

    Args:
        consent: dict avec version, updated_at et choices.
    """
    if not _analyticskit_handlers:
        # Tentative d'auto-découverte si analyticskit est installé
        _try_auto_register()

    for handler in _analyticskit_handlers:
        try:
            handler(consent)
        except Exception as exc:
            logger.warning(
                "xeolux_cookiekit: erreur dans le handler analyticskit '%s': %s",
                getattr(handler, "__name__", repr(handler)),
                exc,
            )


def _try_auto_register() -> None:
    """
    Tente l'auto-enregistrement du handler par défaut de xeolux_analyticskit.

    Conventionnellement, xeolux_analyticskit expose :
        xeolux_analyticskit.cookiekit_handler(consent: dict) -> None
    """
    if not _check_analyticskit_available():
        return
    try:
        from xeolux_analyticskit import cookiekit_handler  # type: ignore[import]

        register_analyticskit_handler(cookiekit_handler)
        logger.info(
            "xeolux_analyticskit.cookiekit_handler auto-enregistré dans cookiekit bridge."
        )
    except (ImportError, AttributeError):
        # analyticskit installé mais handler pas encore implémenté — OK
        pass


def get_bridge_status() -> dict[str, Any]:
    """
    Retourne l'état du bridge pour le debugging et les health-checks.

    Returns:
        dict avec les clés :
          - analyticskit_available (bool)
          - handlers_count (int)
          - handlers (list[str]) — noms des handlers enregistrés
    """
    return {
        "analyticskit_available": _check_analyticskit_available(),
        "handlers_count": len(_analyticskit_handlers),
        "handlers": [
            getattr(h, "__name__", repr(h)) for h in _analyticskit_handlers
        ],
    }


# ── Hook JS attendu côté analyticskit (documentation) ─────────────────────────
#
# Analyticskit devra écouter l'événement JS suivant :
#
#   window.addEventListener("xeolux:cookies:updated", function(event) {
#       var consent = event.detail;
#       // consent.choices.analytics  → true/false
#       // consent.choices.marketing  → true/false
#       // consent.version            → "1.0.0"
#       XeoluxAnalyticsKit.applyConsent(consent.choices);
#   });
#
# Ce contrat d'interface est stable et ne changera pas entre les versions majeures.
