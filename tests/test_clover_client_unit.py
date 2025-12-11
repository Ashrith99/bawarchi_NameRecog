# testing/test_clover_client_unit.py
import pytest


def test_clover_client_initializes_from_env(monkeypatch):
    import clover

    monkeypatch.setenv("CLOVER_MERCHANT_ID", "merchant_123")
    monkeypatch.setenv("CLOVER_ACCESS_TOKEN", "token_abc")
    monkeypatch.setenv("CLOVER_BASE_URL", "https://sandbox.dev.clover.com")

    client = clover.CloverClient()
    assert client.merchant_id == "merchant_123"
    assert client.access_token == "token_abc"
    assert client.base_url == "https://sandbox.dev.clover.com"


def test_clover_client_missing_env_raises(monkeypatch):
    import clover

    monkeypatch.delenv("CLOVER_MERCHANT_ID", raising=False)
    monkeypatch.delenv("CLOVER_ACCESS_TOKEN", raising=False)

    with pytest.raises(ValueError):
        clover.CloverClient()


def test_get_headers_includes_bearer_token(monkeypatch):
    import clover

    monkeypatch.setenv("CLOVER_MERCHANT_ID", "merchant_123")
    monkeypatch.setenv("CLOVER_ACCESS_TOKEN", "token_abc")

    client = clover.CloverClient()
    headers = client._get_headers()

    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer token_abc"
    assert headers["Content-Type"] == "application/json"
