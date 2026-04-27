"""
test_consent.py — Tests sur les modèles et la logique de consentement.
"""
import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestCookieKitConfigModel:
    """Tests du modèle CookieKitConfig."""

    def test_create_config(self):
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig.objects.create(
            enabled=True,
            consent_version="1.0.0",
        )
        assert config.pk is not None
        assert config.consent_version == "1.0.0"

    def test_str_representation(self):
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig(enabled=True, consent_version="2.1.0")
        assert "2.1.0" in str(config)
        assert "Actif" in str(config)

    def test_singleton_validation_blocks_two_active(self):
        """Deux configs actives simultanées doivent être refusées."""
        from xeolux_cookiekit.models import CookieKitConfig

        CookieKitConfig.objects.create(enabled=True, consent_version="1.0.0")
        second = CookieKitConfig(enabled=True, consent_version="1.1.0")
        with pytest.raises(ValidationError):
            second.full_clean()

    def test_singleton_allows_two_inactive(self):
        """Deux configs inactives simultanées sont autorisées."""
        from xeolux_cookiekit.models import CookieKitConfig

        c1 = CookieKitConfig.objects.create(enabled=False, consent_version="1.0.0")
        c2 = CookieKitConfig(enabled=False, consent_version="1.1.0")
        # Ne doit pas lever d'exception
        c2.full_clean()
        c2.save()
        assert CookieKitConfig.objects.count() == 2

    def test_to_settings_dict_structure(self):
        """to_settings_dict() doit retourner un dict avec les clés attendues."""
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig.objects.create(
            enabled=True,
            consent_version="1.5.0",
            google_analytics_enabled=True,
            google_analytics_id="G-TEST123",
        )
        d = config.to_settings_dict()
        assert d["consent_version"] == "1.5.0"
        assert d["integrations"]["google_analytics"]["enabled"] is True
        assert d["integrations"]["google_analytics"]["measurement_id"] == "G-TEST123"
        assert "style" in d
        assert "texts" in d
        assert "cachekit" in d

    def test_cnil_max_age_validation(self):
        """cookie_max_age_days > 395 jours doit lever une ValidationError."""
        from django.core.exceptions import ValidationError
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig(
            enabled=False,
            cookie_max_age_days=400,  # 400 > 395 jours (limite CNIL)
        )
        with pytest.raises(ValidationError, match="395"):
            config.full_clean()

    def test_cnil_max_age_valid_accepts(self):
        """cookie_max_age_days ≤ 395 jours ne doit pas lever d'erreur."""
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig(enabled=False, cookie_max_age_days=180)
        # Ne doit pas lever d'exception sur ce champ
        try:
            config.full_clean()
        except Exception as exc:
            # Seule une erreur sur d'autres champs est acceptable
            assert "cookie_max_age_days" not in str(exc)

    def test_cookie_max_age_conversion(self):
        """cookie_max_age_days doit être converti en secondes dans to_settings_dict."""
        from xeolux_cookiekit.models import CookieKitConfig

        config = CookieKitConfig.objects.create(
            enabled=True,
            cookie_max_age_days=90,
        )
        d = config.to_settings_dict()
        assert d["cookie_max_age"] == 90 * 24 * 60 * 60


@pytest.mark.django_db
class TestCookieCategoryModel:
    """Tests du modèle CookieCategory."""

    def test_create_category(self):
        from xeolux_cookiekit.models import CookieCategory

        cat = CookieCategory.objects.create(
            key="custom_cat",
            label="Personnalisation",
            required=False,
            enabled=True,
        )
        assert cat.pk is not None
        assert str(cat) == "Personnalisation (custom_cat)"

    def test_key_must_be_unique(self):
        from django.db import IntegrityError
        from xeolux_cookiekit.models import CookieCategory

        CookieCategory.objects.create(key="analytics", label="Analytics")
        with pytest.raises(IntegrityError):
            CookieCategory.objects.create(key="analytics", label="Duplicate")


@pytest.mark.django_db
class TestCookieScriptModel:
    """Tests du modèle CookieScript."""

    def test_create_script(self):
        from xeolux_cookiekit.models import CookieScript

        script = CookieScript.objects.create(
            name="Mon script analytics",
            category="analytics",
            position="head",
            script='<script>console.log("test")</script>',
        )
        assert script.pk is not None
        assert "Mon script analytics" in str(script)

    def test_str_shows_status(self):
        from xeolux_cookiekit.models import CookieScript

        active_script = CookieScript(
            name="Script actif",
            enabled=True,
            category="analytics",
            position="head",
            script="",
        )
        inactive_script = CookieScript(
            name="Script inactif",
            enabled=False,
            category="analytics",
            position="head",
            script="",
        )
        assert "✓" in str(active_script)
        assert "✗" in str(inactive_script)


@pytest.mark.django_db
class TestConsentVersionLogic:
    """Tests sur la logique de version de consentement."""

    def test_version_from_settings_is_used(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        # La version doit être celle de settings.py (1.0.0 dans conftest)
        assert config["consent_version"] == "1.0.0"

    def test_config_source_settings_only_no_admin_call(self):
        """Avec config_source=settings_only, _get_admin_config n'est pas appelé."""
        from unittest.mock import patch
        from xeolux_cookiekit.conf import get_cookiekit_config

        with patch("xeolux_cookiekit.conf._get_admin_config") as mock_admin:
            get_cookiekit_config()
            mock_admin.assert_not_called()

    def test_necessary_category_always_required(self):
        from xeolux_cookiekit.conf import get_cookiekit_config

        config = get_cookiekit_config()
        necessary = config["categories"].get("necessary", {})
        assert necessary.get("required") is True
        assert necessary.get("enabled") is True
