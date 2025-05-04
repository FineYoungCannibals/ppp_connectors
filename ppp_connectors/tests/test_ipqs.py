import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import ipqs


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("IPQS_API_KEY", "fake_api_key")


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"success": True, "unsafe": False}
    return mock


@patch("ppp_connectors.connectors.ipqs.make_request")
def test_ipqs_malicious_url_success(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response

    query = "http://example.com"
    response = ipqs.ipqs_malicious_url(query)

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_make_request.assert_called_once()


@patch("ppp_connectors.connectors.ipqs.make_request")
def test_ipqs_malicious_url_passes_encoded_url(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response

    query = "http://example.com/?q=bad stuff"
    response = ipqs.ipqs_malicious_url(query, custom_param="value")

    called_args = mock_make_request.call_args[1]
    assert called_args["json"]["url"] == "http%3A//example.com/%3Fq%3Dbad%20stuff"
    assert called_args["json"]["custom_param"] == "value"
    assert response.status_code == 200


def test_ipqs_malicious_url_missing_api_key():
    with patch.object(ipqs, "env_config", {}):
        with pytest.raises(SystemExit):
            ipqs.ipqs_malicious_url("http://example.com")
