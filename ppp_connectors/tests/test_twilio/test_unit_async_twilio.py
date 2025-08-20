import pytest
import httpx
from unittest.mock import patch, AsyncMock
from ppp_connectors.api_connectors.twilio import AsyncTwilioConnector

@pytest.mark.asyncio
async def test_async_init_with_env(monkeypatch):
    monkeypatch.setenv("TWILIO_API_SID", "sid")
    monkeypatch.setenv("TWILIO_API_SECRET", "secret")

    connector = AsyncTwilioConnector(load_env_vars=True)
    assert connector.api_sid == "sid"
    assert connector.api_secret == "secret"

@pytest.mark.asyncio
async def test_async_lookup_phone_raises_for_invalid_packages():
    connector = AsyncTwilioConnector(api_sid="a", api_secret="b")
    with pytest.raises(ValueError, match="Invalid data packages: badpkg"):
        await connector.lookup_phone("+14155552671", data_packages=["badpkg"])

@patch("ppp_connectors.api_connectors.twilio.AsyncTwilioConnector._make_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_lookup_phone_calls_make_request(mock_request):
    mock_resp = httpx.Response(200, content=b'{"valid": true}')
    mock_request.return_value = mock_resp

    connector = AsyncTwilioConnector(api_sid="a", api_secret="b")
    result = await connector.lookup_phone("+14155552671", data_packages=["caller_name"])

    assert result.status_code == 200
    assert mock_request.await_count == 1
    args, kwargs = mock_request.call_args
    assert kwargs["endpoint"].endswith("+14155552671")
    assert "caller_name" in kwargs["params"]["Fields"]