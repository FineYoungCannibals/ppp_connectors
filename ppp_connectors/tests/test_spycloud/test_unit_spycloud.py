import json
import httpx
import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.spycloud import SpycloudConnector


def test_init_with_api_key():
    connector = SpycloudConnector(sip_key="sip", ato_key="ato", inv_key="inv")
    assert connector.sip_key == "sip"
    assert connector.ato_key == "ato"
    assert connector.inv_key == "inv"


@patch.dict("os.environ", {"SPYCLOUD_API_ATO_KEY": "env_key"}, clear=True)
def test_init_with_env_key():
    connector = SpycloudConnector(load_env_vars=True)
    assert connector.ato_key == "env_key"


@patch("ppp_connectors.api_connectors.broker.combine_env_configs", return_value={})
def test_init_missing_key(mock_env):
    connector = SpycloudConnector(load_env_vars=True)
    with pytest.raises(ValueError, match="SPYCLOUD_API_ATO_KEY is required for this request"):
        connector.ato_search(search_type="email", query="test@example.com")


@patch("ppp_connectors.api_connectors.spycloud.SpycloudConnector._make_request")
def test_ato_search(mock_request):
    # Build a real httpx.Response to match new return type (raw Response)
    request = httpx.Request("GET", "https://api.spycloud.io/sp-v2/breach/data/emails/test@example.com")
    payload = {"results": []}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_request.return_value = mock_response

    connector = SpycloudConnector(ato_key="test_key")
    result = connector.ato_search(search_type="ip", query="test@example.com")

    mock_request.assert_called_once()
    assert isinstance(result, httpx.Response)
    assert result.json() == payload