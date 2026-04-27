"""
test_conf.py — Tests de la logique de fusion de configuration.
"""
import pytest
from unittest.mock import patch


@pytest.mark.django_db
class TestDeepMerge:
    """Tests de la fonction _deep_merge."""

    def test_merge_scalars(self):
        from xeolux_cookiekit.conf import _deep_merge

        base = {"a": 1, "b": 2}
        override = {"b": 99, "c": 3}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 99, "c": 3}

    def test_merge_nested_dicts(self):
        from xeolux_cookiekit.conf import _deep_merge

        base = {"style": {"color": "red", "size": "small"}}
        override = {"style": {"color": "blue"}}
        result = _deep_merge(base, override)
        assert result["style"]["color"] == "blue"
        assert result["style"]["size"] == "small"

    def test_merge_does_not_mutate_base(self):
        from xeolux_cookiekit.conf import _deep_merge

        base = {"a": {"x": 1}}
        override = {"a": {"x": 2}}
        _deep_merge(base, override)
        assert base["a"]["x"] == 1

    def test_override_replaces_non_dict_with_dict(self):
        from xeolux_cookiekit.conf import _deep_merge

        base = {"a": "string"}
        override = {"a": {"nested": True}}
        result = _deep_merge(base, override)
        assert result["a"] == {"nested": True}


@pytest.mark.django_db
class TestGetCookiekitConfig:
    """Tests de get_cookiekit_config()."""

    def test_returns_dict(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert isinstance(config, dict)

    def test_enabled_from_settings(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["enabled"] is True

    def test_consent_version_from_settings(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["consent_version"] == "1.0.0"

    def test_style_merge_from_settings(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        # La couleur primaire vient de settings
        assert config["style"]["primary_color"] == "#ff6b00"
        # Les autres valeurs viennent des defaults
        assert "background_color" in config["style"]

    def test_defaults_present(self):
        from xeolux_cookiekit.conf import get_cookiekit_config
        from xeolux_cookiekit.defaults import COOKIEKIT_DEFAULTS

        config = get_cookiekit_config()
        # Toutes les clés des defaults doivent être présentes
        for key in COOKIEKIT_DEFAULTS:
            assert key in config, f"Clé '{key}' manquante dans la config"

    def test_categories_include_necessary(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert "necessary" in config["categories"]
        assert config["categories"]["necessary"]["required"] is True

    def test_settings_only_ignores_admin(self):
        """Avec config_source=settings_only, l'admin n'est jamais consulté."""
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_admin_config") as mock_admin:
            mock_admin.return_value = {"consent_version": "99.0.0"}
            config = get_cookiekit_config()
            # L'admin ne doit pas être appelé avec config_source=settings_only
            mock_admin.assert_not_called()
            assert config["consent_version"] == "1.0.0"

    def test_admin_fallback_applies_admin_config(self, settings):
        """Avec config_source=admin_fallback_settings, l'admin override settings."""
        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "consent_version": "1.0.0",
            "config_source": "admin_fallback_settings",
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_admin_config") as mock_admin:
            mock_admin.return_value = {"consent_version": "2.5.0"}
            config = get_cookiekit_config()
            assert config["consent_version"] == "2.5.0"

    def test_no_error_when_db_unavailable(self, settings):
        """Pas d'erreur si la table admin n'existe pas."""
        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "consent_version": "1.0.0",
            "config_source": "admin_fallback_settings",
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_admin_config") as mock_admin:
            mock_admin.return_value = None
            # Ne doit pas lever d'exception
            config = get_cookiekit_config()
            assert config["consent_version"] == "1.0.0"

    def test_cachekit_version_sync(self, settings):
        """La version cachekit remplace consent_version si disponible."""
        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "consent_version": "1.0.0",
            "config_source": "settings_only",
            "cachekit": {
                "enabled": True,
                "sync_cookie_version": True,
                "version_key": "cookiekit",
            },
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_cachekit_version") as mock_ck:
            mock_ck.return_value = "3.1.0"
            config = get_cookiekit_config()
            assert config["consent_version"] == "3.1.0"

    def test_cachekit_unavailable_fallback(self, settings):
        """Sans cachekit disponible, on utilise consent_version."""
        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "consent_version": "1.0.0",
            "config_source": "settings_only",
            "cachekit": {
                "enabled": True,
                "sync_cookie_version": True,
                "version_key": "cookiekit",
            },
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_cachekit_version") as mock_ck:
            mock_ck.return_value = None
            config = get_cookiekit_config()
            assert config["consent_version"] == "1.0.0"

    def test_minimal_settings_only_enabled(self, settings):
        """settings.py avec uniquement enabled:True — tous les defaults sont appliqués."""
        settings.XEOLUX_COOKIEKIT = {"enabled": True}
        from xeolux_cookiekit.conf import get_cookiekit_config
        from xeolux_cookiekit.defaults import COOKIEKIT_DEFAULTS

        config = get_cookiekit_config()
        assert config["enabled"] is True
        # Vérifier que tous les defaults sont présents
        for key in COOKIEKIT_DEFAULTS:
            assert key in config

    def test_minimal_settings_only_disabled(self, settings):
        """settings.py avec enabled:False désactive le bandeau."""
        settings.XEOLUX_COOKIEKIT = {"enabled": False}
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["enabled"] is False


@pytest.mark.django_db
class TestRGPDCompliance:
    """Tests de conformité RGPD/CNIL."""

    def test_analytics_disabled_by_default(self):
        """La catégorie analytics doit être opt-in (enabled: False) par défaut."""
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["categories"]["analytics"]["enabled"] is False, (
            "RGPD/CNIL : analytics doit être opt-in (enabled=False par défaut)"
        )

    def test_marketing_disabled_by_default(self):
        """La catégorie marketing doit être opt-in par défaut."""
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["categories"]["marketing"]["enabled"] is False

    def test_necessary_always_required(self):
        """Nécessaires : required=True, enabled=True."""
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        necessary = config["categories"]["necessary"]
        assert necessary["required"] is True
        assert necessary["enabled"] is True

    def test_cookie_max_age_clamped_at_cnil_limit(self, settings):
        """Un cookie_max_age > 395 jours doit être plafonné à 395 jours."""
        from xeolux_cookiekit.defaults import CNIL_MAX_COOKIE_AGE_SECONDS

        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "config_source": "settings_only",
            "cookie_max_age": 999 * 24 * 60 * 60,  # 999 jours → illégal CNIL
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["cookie_max_age"] <= CNIL_MAX_COOKIE_AGE_SECONDS, (
            "CNIL : cookie_max_age ne doit pas dépasser 395 jours (13 mois)"
        )

    def test_cookie_max_age_valid_unchanged(self, settings):
        """Un cookie_max_age ≤ 395 jours ne doit pas être modifié."""
        settings.XEOLUX_COOKIEKIT = {
            "enabled": True,
            "config_source": "settings_only",
            "cookie_max_age": 180 * 24 * 60 * 60,  # 180 jours — OK
        }
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert config["cookie_max_age"] == 180 * 24 * 60 * 60

    def test_analyticskit_section_present_in_config(self):
        """La section analyticskit doit être présente dans la config."""
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        assert "analyticskit" in config
        assert "enabled" in config["analyticskit"]
        assert "forward_consent" in config["analyticskit"]


@pytest.mark.django_db
class TestAnalyticsKitBridge:
    """Tests du bridge analyticskit."""

    def test_bridge_status_returns_dict(self):
        from xeolux_cookiekit.analyticskit_bridge import get_bridge_status

        status = get_bridge_status()
        assert isinstance(status, dict)
        assert "analyticskit_available" in status
        assert "handlers_count" in status
        assert "handlers" in status

    def test_analyticskit_not_available_without_install(self):
        from xeolux_cookiekit.analyticskit_bridge import get_bridge_status

        status = get_bridge_status()
        # Dans les tests, analyticskit n'est pas installé
        assert status["analyticskit_available"] is False

    def test_register_and_unregister_handler(self):
        from xeolux_cookiekit.analyticskit_bridge import (
            _analyticskit_handlers,
            register_analyticskit_handler,
            unregister_analyticskit_handler,
        )

        def my_handler(consent: dict) -> None:
            pass

        register_analyticskit_handler(my_handler)
        assert my_handler in _analyticskit_handlers

        unregister_analyticskit_handler(my_handler)
        assert my_handler not in _analyticskit_handlers

    def test_register_handler_no_duplicate(self):
        from xeolux_cookiekit.analyticskit_bridge import (
            _analyticskit_handlers,
            register_analyticskit_handler,
            unregister_analyticskit_handler,
        )

        def my_handler(consent: dict) -> None:
            pass

        register_analyticskit_handler(my_handler)
        register_analyticskit_handler(my_handler)  # Double enregistrement
        count = _analyticskit_handlers.count(my_handler)
        assert count == 1

        unregister_analyticskit_handler(my_handler)

    def test_dispatch_calls_handler(self):
        from xeolux_cookiekit.analyticskit_bridge import (
            dispatch_consent_to_analyticskit,
            register_analyticskit_handler,
            unregister_analyticskit_handler,
        )

        received = []

        def my_handler(consent: dict) -> None:
            received.append(consent)

        register_analyticskit_handler(my_handler)
        try:
            consent = {
                "version": "1.0.0",
                "updated_at": "2026-04-27T12:00:00Z",
                "choices": {"necessary": True, "analytics": True, "marketing": False},
            }
            dispatch_consent_to_analyticskit(consent)
            assert len(received) == 1
            assert received[0]["choices"]["analytics"] is True
        finally:
            unregister_analyticskit_handler(my_handler)

    def test_dispatch_survives_handler_error(self):
        """Une exception dans un handler ne doit pas bloquer le flux."""
        from xeolux_cookiekit.analyticskit_bridge import (
            dispatch_consent_to_analyticskit,
            register_analyticskit_handler,
            unregister_analyticskit_handler,
        )

        def broken_handler(consent: dict) -> None:
            raise RuntimeError("Simulated error")

        register_analyticskit_handler(broken_handler)
        try:
            # Ne doit pas lever d'exception
            dispatch_consent_to_analyticskit({"version": "1.0.0", "choices": {}})
        finally:
            unregister_analyticskit_handler(broken_handler)
