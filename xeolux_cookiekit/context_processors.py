"""
context_processors.py — Injecte la configuration CookieKit dans le contexte des templates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def cookiekit_config(request: "HttpRequest") -> dict:
    """
    Injecte `cookiekit_config` dans le contexte de tous les templates.

    Usage dans les templates :
        {{ cookiekit_config.consent_version }}
        {{ cookiekit_config.texts.title }}
    """
    try:
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
    except Exception:
        config = {}

    return {"cookiekit_config": config}
