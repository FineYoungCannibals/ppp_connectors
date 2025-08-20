import pytest
import httpx
from ppp_connectors.api_connectors.spycloud import AsyncSpycloudConnector

@pytest.mark.asyncio
async def test_async_init_with_env_keys(monkeypatch):
    monkeypatch.setenv("SPYCLOUD_API_SIP_KEY", "sip")
    monkeypatch.setenv("SPYCLOUD_API_ATO_KEY", "ato")
    monkeypatch.setenv("SPYCLOUD_API_INV_KEY", "inv")

    conn = AsyncSpycloudConnector(load_env_vars=True)
    assert conn.sip_key == "sip"
    assert conn.ato_key == "ato"
    assert conn.inv_key == "inv"

@pytest.mark.asyncio
async def test_async_sip_cookie_domains_sends(mocker):
    mock_response = mocker.AsyncMock(spec=httpx.Response)
    request = mocker.patch("httpx.AsyncClient.request", return_value=mock_response)

    connector = AsyncSpycloudConnector(sip_key="abc123")
    result = await connector.sip_cookie_domains("test.com", q="xyz")

    assert result is mock_response
    request.assert_called_once()
    args, kwargs = request.call_args
    assert kwargs["url"].endswith("/sip-v1/breach/data/cookie-domains/test.com")
    assert kwargs["headers"]["x-api-key"] == "abc123"
    assert kwargs["params"]["q"] == "xyz"

@pytest.mark.asyncio
async def test_async_ato_search_ip(mocker):
    mock_response = mocker.AsyncMock(spec=httpx.Response)
    mocker.patch("httpx.AsyncClient.request", return_value=mock_response)

    connector = AsyncSpycloudConnector(ato_key="abc123")
    resp = await connector.ato_search("ip", "1.2.3.4")
    assert resp is mock_response

@pytest.mark.asyncio
async def test_async_investigations_invalid_type_raises():
    conn = AsyncSpycloudConnector(inv_key="abc")
    with pytest.raises(ValueError):
        await conn.investigations_search("not-a-real-type", "foo")