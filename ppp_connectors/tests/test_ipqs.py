import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import ipqs


def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"success": True, "unsafe": False}
    return mock


@patch("ppp_connectors.connectors.ipqs.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.ipqs.check_required_env_vars")
@patch("ppp_connectors.connectors.ipqs.combine_env_configs", return_value={
    "IPQS_API_KEY": "fake"
})
def test_ipqs_malicious_url_success(mock_env, mock_check, mock_request):
    query = "http://example.com"
    response = ipqs.ipqs_malicious_url(query)

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.ipqs.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.ipqs.check_required_env_vars")
@patch("ppp_connectors.connectors.ipqs.combine_env_configs", return_value={
    "IPQS_API_KEY": "fake"
})
def test_ipqs_malicious_url_passes_encoded_url(mock_env, mock_check, mock_request):
    query = "http://example.com/?q=bad stuff"
    response = ipqs.ipqs_malicious_url(query, custom_param="value")

    called_args = mock_request.call_args[1]
    assert called_args["json"]["url"] == "http%3A//example.com/%3Fq%3Dbad%20stuff"
    assert called_args["json"]["custom_param"] == "value"
    assert response.status_code == 200


@patch("ppp_connectors.connectors.ipqs.combine_env_configs", return_value={})
def test_ipqs_malicious_url_missing_api_key(mock_env):
    with pytest.raises(SystemExit):
        ipqs.ipqs_malicious_url("http://example.com")