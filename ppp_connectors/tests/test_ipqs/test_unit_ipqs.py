import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.ipqs import IPQSConnector


def test_init_with_api_key():
    connector = IPQSConnector(api_key="test_key")
    assert connector.api_key == "test_key"
    assert connector.headers["Content-Type"] == "application/json"


def test_init_with_env_key():
    with patch.dict("os.environ", {"IPQS_API_KEY": "env_key"}):
        connector = IPQSConnector(load_env_vars=True)
        assert connector.api_key == "env_key"


def test_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="API key is required"):
            IPQSConnector()


@patch("ppp_connectors.api_connectors.ipqs.IPQSConnector.post")
def test_malicious_url(mock_post):
    # Mock a response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "domain": "example.com"}
    mock_post.return_value = mock_response

    connector = IPQSConnector(api_key="test_key")
    result = connector.malicious_url("example.com")

    mock_post.assert_called_once()
    assert result == {"success": True, "domain": "example.com"}
