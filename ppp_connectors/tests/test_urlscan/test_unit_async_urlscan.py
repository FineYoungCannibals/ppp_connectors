import pytest
from httpx import Response
from httpx import Request
from ppp_connectors.api_connectors.urlscan import AsyncURLScanConnector

@pytest.mark.asyncio
async def test_async_init_with_api_key():
    connector = AsyncURLScanConnector(api_key="testkey")
    assert connector.api_key == "testkey"
    assert connector.headers["API-Key"] == "testkey"

@pytest.mark.asyncio
async def test_async_init_with_env(monkeypatch):
    monkeypatch.setenv("URLSCAN_API_KEY", "envkey")
    connector = AsyncURLScanConnector(load_env_vars=True)
    assert connector.api_key == "envkey"
    assert connector.headers["API-Key"] == "envkey"

@pytest.mark.asyncio
async def test_async_init_missing_key_raises(monkeypatch):
    monkeypatch.delenv("URLSCAN_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key is required for AsyncURLScanConnector"):
        AsyncURLScanConnector()

@pytest.mark.asyncio
async def test_async_search_makes_expected_call(monkeypatch):
    connector = AsyncURLScanConnector(api_key="testkey")

    async def mock_get(path, params=None):
        assert path == "/api/v1/search/"
        assert params["q"] == "example.com"
        return Response(200, request=Request("GET", path))

    connector.get = mock_get
    resp = await connector.search("example.com")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_async_scan_makes_expected_call(monkeypatch):
    connector = AsyncURLScanConnector(api_key="testkey")

    async def mock_post(path, json=None):
        assert path == "/api/v1/scan"
        assert json["url"] == "http://example.com"
        return Response(200, request=Request("POST", path))

    connector.post = mock_post
    resp = await connector.scan("http://example.com")
    assert resp.status_code == 200