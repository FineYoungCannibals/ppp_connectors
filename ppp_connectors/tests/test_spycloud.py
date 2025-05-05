import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import spycloud


def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"result": "ok"}
    return mock


@patch("ppp_connectors.connectors.spycloud.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.spycloud.check_required_env_vars")
@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_SIP_KEY": "fake"
})
def test_spycloud_sip_cookie_domains(mock_env, mock_check, mock_request):
    resp = spycloud.spycloud_sip_cookie_domains("example.com")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.spycloud.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.spycloud.check_required_env_vars")
@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_ATO_KEY": "fake"
})
def test_spycloud_ato_breach_catalog(mock_env, mock_check, mock_request):
    resp = spycloud.spycloud_ato_breach_catalog("test")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.spycloud.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.spycloud.check_required_env_vars")
@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_ATO_KEY": "fake"
})
def test_spycloud_ato_search_valid(mock_env, mock_check, mock_request):
    resp = spycloud.spycloud_ato_search("email", "test@example.com")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_ATO_KEY": "fake"
})
def test_spycloud_ato_search_invalid_type(mock_env):
    with pytest.raises(SystemExit):
        spycloud.spycloud_ato_search("invalid", "query")


@patch("ppp_connectors.connectors.spycloud.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.spycloud.check_required_env_vars")
@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_INV_KEY": "fake"
})
def test_spycloud_inv_search_valid(mock_env, mock_check, mock_request):
    resp = spycloud.spycloud_inv_search("domain", "example.com")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.spycloud.combine_env_configs", return_value={
    "SPYCLOUD_API_INV_KEY": "fake"
})
def test_spycloud_inv_search_invalid_type(mock_env):
    with pytest.raises(SystemExit):
        spycloud.spycloud_inv_search("invalid-type", "query")