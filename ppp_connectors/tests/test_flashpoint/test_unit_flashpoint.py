


import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.flashpoint import FlashpointConnector

def test_init_with_api_key():
    connector = FlashpointConnector(api_key="test_token")
    assert connector.api_key == "test_token"
    assert connector.headers["Authorization"] == "Bearer test_token"


@patch.dict("os.environ", {"FLASHPOINT_API_KEY": "env_token"}, clear=True)
def test_init_with_env_key():
    connector = FlashpointConnector(load_env_vars=True)
    assert connector.api_key == "env_token"
    assert connector.headers["Authorization"] == "Bearer env_token"


def test_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FLASHPOINT_API_KEY is required"):
            FlashpointConnector()


@patch("ppp_connectors.api_connectors.flashpoint.FlashpointConnector.post")
def test_search_fraud(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "data": []}
    mock_post.return_value = mock_response

    connector = FlashpointConnector(api_key="mock_token")
    result = connector.search_fraud("credential stuffing")

    assert result == {"success": True, "data": []}
    mock_post.assert_called_once()