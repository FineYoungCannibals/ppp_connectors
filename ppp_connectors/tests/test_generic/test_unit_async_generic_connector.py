import pytest
import httpx
from unittest.mock import AsyncMock, patch
from ppp_connectors.api_connectors.generic import AsyncGenericConnector


@pytest.mark.asyncio
async def test_async_init_sets_base_url():
    connector = AsyncGenericConnector(base_url="https://example.com")
    assert connector.base_url == "https://example.com"


@patch("ppp_connectors.api_connectors.generic.AsyncGenericConnector._make_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_get_request(mock_make_request):
    mock_response = httpx.Response(200, json={"result": "ok"})
    mock_make_request.return_value = mock_response

    connector = AsyncGenericConnector(base_url="https://example.com")
    response = await connector.request("GET", "/test")

    assert response.status_code == 200
    assert response.json() == {"result": "ok"}
    mock_make_request.assert_awaited_once_with(
        method="GET",
        endpoint="/test",
        headers=connector.headers,
        params=None,
        json=None,
        auth=None,
        retry_kwargs=None,
    )


@patch("ppp_connectors.api_connectors.generic.AsyncGenericConnector._make_request", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_post_request(mock_make_request):
    mock_response = httpx.Response(200, json={"posted": True})
    mock_make_request.return_value = mock_response

    connector = AsyncGenericConnector(base_url="https://example.com")
    response = await connector.request("POST", "/submit", json={"key": "value"})

    assert response.status_code == 200
    assert response.json() == {"posted": True}
    mock_make_request.assert_awaited_once_with(
        method="POST",
        endpoint="/submit",
        headers=connector.headers,
        params=None,
        json={"key": "value"},
        auth=None,
        retry_kwargs=None,
    )