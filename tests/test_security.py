"""
test_security.py — Tests du module security.py (HMAC, validation, sanitization).
"""
import json
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_secret_key(settings):
    settings.SECRET_KEY = "xeolux-cookiekit-test-secret-key-12345"
    return settings.SECRET_KEY


class TestSignature:
    """Tests de la signature HMAC."""

    def test_sign_and_verify_roundtrip(self, mock_secret_key):
        from xeolux_cookiekit.security import _sign_payload, _verify_signature

        payload = '{"version":"1.0.0","choices":{"necessary":true}}'
        sig = _sign_payload(payload)
        assert _verify_signature(payload, sig) is True

    def test_tampered_payload_fails(self, mock_secret_key):
        from xeolux_cookiekit.security import _sign_payload, _verify_signature

        payload = '{"version":"1.0.0","choices":{"necessary":true}}'
        sig = _sign_payload(payload)
        tampered = '{"version":"1.0.0","choices":{"necessary":true,"analytics":true}}'
        assert _verify_signature(tampered, sig) is False

    def test_wrong_signature_fails(self, mock_secret_key):
        from xeolux_cookiekit.security import _verify_signature

        payload = '{"version":"1.0.0","choices":{"necessary":true}}'
        assert _verify_signature(payload, "deadbeef" * 8) is False

    def test_empty_signature_fails(self, mock_secret_key):
        from xeolux_cookiekit.security import _verify_signature

        payload = '{"version":"1.0.0","choices":{"necessary":true}}'
        assert _verify_signature(payload, "") is False

    def test_signature_constant_time(self, mock_secret_key):
        """Vérifie que la comparaison est à temps constant (hmac.compare_digest)."""
        from xeolux_cookiekit.security import _sign_payload, _verify_signature
        import hmac as hmac_module

        payload = '{"test":"data"}'
        sig = _sign_payload(payload)
        # compare_digest doit être utilisé — pas de raccourci ==
        with patch.object(hmac_module, "compare_digest", wraps=hmac_module.compare_digest) as mock_cd:
            _verify_signature(payload, sig)
            mock_cd.assert_called_once()


class TestPayloadValidation:
    """Tests de validation du payload de consentement."""

    def test_valid_payload(self):
        from xeolux_cookiekit.security import _validate_consent_payload

        data = {
            "version": "1.0.0",
            "updated_at": "2026-04-27T12:00:00Z",
            "choices": {"necessary": True, "analytics": False},
        }
        result = _validate_consent_payload(data)
        assert result["version"] == "1.0.0"
        assert result["choices"]["necessary"] is True

    def test_necessary_always_true(self):
        """necessary doit toujours être True même si fourni à False."""
        from xeolux_cookiekit.security import _validate_consent_payload

        data = {
            "version": "1.0.0",
            "choices": {"necessary": False, "analytics": True},
        }
        result = _validate_consent_payload(data)
        assert result["choices"]["necessary"] is True

    def test_invalid_category_key_ignored(self):
        """Les clés de catégories invalides doivent être ignorées silencieusement."""
        from xeolux_cookiekit.security import _validate_consent_payload

        data = {
            "version": "1.0.0",
            "choices": {
                "necessary": True,
                "valid_key": True,
                "<script>alert(1)</script>": True,  # Injection tentée
                "../../etc/passwd": False,           # Path traversal tenté
                "a" * 51: True,                      # Clé trop longue
            },
        }
        result = _validate_consent_payload(data)
        assert "<script>alert(1)</script>" not in result["choices"]
        assert "../../etc/passwd" not in result["choices"]
        assert ("a" * 51) not in result["choices"]
        assert "valid_key" in result["choices"]

    def test_non_boolean_values_coerced(self):
        """Les valeurs non-booléennes doivent être converties en bool."""
        from xeolux_cookiekit.security import _validate_consent_payload

        data = {
            "version": "1.0.0",
            "choices": {"analytics": 1, "marketing": 0, "necessary": "yes"},
        }
        result = _validate_consent_payload(data)
        assert result["choices"]["analytics"] is True
        assert result["choices"]["marketing"] is False
        # necessary toujours True
        assert result["choices"]["necessary"] is True

    def test_missing_version_raises(self):
        from xeolux_cookiekit.security import _validate_consent_payload, ConsentVerificationError

        with pytest.raises(ConsentVerificationError, match="version"):
            _validate_consent_payload({"choices": {"necessary": True}})

    def test_missing_choices_raises(self):
        from xeolux_cookiekit.security import _validate_consent_payload, ConsentVerificationError

        with pytest.raises(ConsentVerificationError, match="choices"):
            _validate_consent_payload({"version": "1.0.0"})

    def test_not_a_dict_raises(self):
        from xeolux_cookiekit.security import _validate_consent_payload, ConsentVerificationError

        with pytest.raises(ConsentVerificationError):
            _validate_consent_payload(["not", "a", "dict"])

    def test_too_many_categories_raises(self):
        from xeolux_cookiekit.security import _validate_consent_payload, ConsentVerificationError, MAX_CATEGORIES

        choices = {f"cat_{i}": True for i in range(MAX_CATEGORIES + 1)}
        with pytest.raises(ConsentVerificationError, match="Trop"):
            _validate_consent_payload({"version": "1.0.0", "choices": choices})

    def test_invalid_version_format_raises(self):
        from xeolux_cookiekit.security import _validate_consent_payload, ConsentVerificationError

        with pytest.raises(ConsentVerificationError, match="Version"):
            _validate_consent_payload({
                "version": "<script>x</script>",
                "choices": {"necessary": True},
            })


@pytest.mark.django_db
class TestGetVerifiedConsent:
    """Tests de get_verified_consent() et verify_consent_request()."""

    def _make_request(self, cookies: dict):
        """Crée un faux objet request avec des cookies."""
        class FakeRequest:
            COOKIES = cookies
        return FakeRequest()

    def test_no_cookie_returns_none(self, mock_secret_key):
        from xeolux_cookiekit.security import get_verified_consent

        request = self._make_request({})
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is None

    def test_valid_unsigned_cookie(self, mock_secret_key):
        """Cookie valide sans signature → retourne VerifiedConsent avec is_signed=False."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent

        payload = json.dumps({
            "version": "1.0.0",
            "updated_at": "2026-04-27T12:00:00Z",
            "choices": {"necessary": True, "analytics": False},
        })
        request = self._make_request({"xeolux_cookie_consent": quote(payload)})
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is not None
        assert result.version == "1.0.0"
        assert result.is_signed is False
        assert result.choices["necessary"] is True

    def test_valid_signed_cookie(self, mock_secret_key):
        """Cookie avec signature valide → is_signed=True."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent, _sign_payload

        payload = json.dumps({
            "version": "1.0.0",
            "choices": {"necessary": True, "analytics": True},
        })
        sig = _sign_payload(payload)
        request = self._make_request({
            "xeolux_cookie_consent": quote(payload),
            "xeolux_cookie_consent_sig": sig,
        })
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is not None
        assert result.is_signed is True
        assert result.choices["analytics"] is True

    def test_tampered_cookie_with_signature_returns_none(self, mock_secret_key):
        """Cookie falsifié avec signature originale → None."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent, _sign_payload

        original_payload = json.dumps({
            "version": "1.0.0",
            "choices": {"necessary": True, "analytics": False},
        })
        sig = _sign_payload(original_payload)

        # L'utilisateur modifie le cookie pour activer analytics
        tampered_payload = json.dumps({
            "version": "1.0.0",
            "choices": {"necessary": True, "analytics": True},
        })
        request = self._make_request({
            "xeolux_cookie_consent": quote(tampered_payload),
            "xeolux_cookie_consent_sig": sig,
        })
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is None

    def test_oversized_cookie_returns_none(self, mock_secret_key):
        """Cookie trop grand → None."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent, MAX_PAYLOAD_BYTES

        big_payload = "x" * (MAX_PAYLOAD_BYTES + 1)
        request = self._make_request({"xeolux_cookie_consent": quote(big_payload)})
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is None

    def test_invalid_json_returns_none(self, mock_secret_key):
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent

        request = self._make_request({"xeolux_cookie_consent": quote("not{json}")})
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is None

    def test_raise_on_invalid_tampered(self, mock_secret_key):
        """Avec raise_on_invalid=True, lève ConsentVerificationError."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import (
            get_verified_consent, _sign_payload, ConsentVerificationError
        )

        original = json.dumps({"version": "1.0.0", "choices": {"necessary": True}})
        sig = _sign_payload(original)
        tampered = json.dumps({"version": "1.0.0", "choices": {"necessary": True, "analytics": True}})

        request = self._make_request({
            "xeolux_cookie_consent": quote(tampered),
            "xeolux_cookie_consent_sig": sig,
        })
        with pytest.raises(ConsentVerificationError):
            get_verified_consent(request, cookie_name="xeolux_cookie_consent", raise_on_invalid=True)

    def test_verified_consent_has_method(self, mock_secret_key):
        """VerifiedConsent.has() valide la clé avant de retourner le consentement."""
        from urllib.parse import quote
        from xeolux_cookiekit.security import get_verified_consent

        payload = json.dumps({
            "version": "1.0.0",
            "choices": {"necessary": True, "analytics": True},
        })
        request = self._make_request({"xeolux_cookie_consent": quote(payload)})
        result = get_verified_consent(request, cookie_name="xeolux_cookie_consent")
        assert result is not None
        assert result.has("analytics") is True
        assert result.has("marketing") is False
        # Clé invalide → False (pas d'exception)
        assert result.has("<script>") is False
        assert result.has("") is False
