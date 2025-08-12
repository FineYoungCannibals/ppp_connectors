import httpx
import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.urlscan import URLScanConnector

def test_init_with_api_key():
    connector = URLScanConnector(api_key="test_key")
    assert connector.api_key == "test_key"

@patch.dict("os.environ", {"URLSCAN_API_KEY": "env_key"}, clear=True)
def test_init_with_env_key():
    connector = URLScanConnector(load_env_vars=True)
    assert connector.api_key == "env_key"

@patch("ppp_connectors.api_connectors.broker.combine_env_configs", return_value={})
def test_init_missing_auth_keys(mock_env):
    with pytest.raises(ValueError, match="API key is required for URLScanConnector"):
        URLScanConnector(load_env_vars=True)

@patch("ppp_connectors.api_connectors.urlscan.URLScanConnector.get")
def test_results(mock_get):
    import json

    # Build a real httpx.Response to match the new return type
    request = httpx.Request("GET", "https://urlscan.io/api/v1/result/abc123")
    payload = {"task": "test"}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_get.return_value = mock_response

    connector = URLScanConnector(api_key="test_key")
    result = connector.results("abc123")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload