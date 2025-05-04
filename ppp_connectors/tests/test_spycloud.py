import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import spycloud


@patch.object(spycloud, "env_config", {"SPYCLOUD_API_SIP_KEY": "fake"})
@patch("ppp_connectors.connectors.spycloud.make_request")
def test_spycloud_sip_cookie_domains(mock_make_request):
    mock_resp = MagicMock()
    mock_make_request.return_value = mock_resp
    resp = spycloud.spycloud_sip_cookie_domains("example.com")
    assert resp == mock_resp
    mock_make_request.assert_called_once()


@patch.object(spycloud, "env_config", {"SPYCLOUD_API_ATO_KEY": "fake"})
@patch("ppp_connectors.connectors.spycloud.make_request")
def test_spycloud_ato_breach_catalog(mock_make_request):
    mock_resp = MagicMock()
    mock_make_request.return_value = mock_resp
    resp = spycloud.spycloud_ato_breach_catalog("test")
    assert resp == mock_resp
    mock_make_request.assert_called_once()


@patch.object(spycloud, "env_config", {"SPYCLOUD_API_ATO_KEY": "fake"})
@patch("ppp_connectors.connectors.spycloud.make_request")
def test_spycloud_ato_search_valid(mock_make_request):
    mock_resp = MagicMock()
    mock_make_request.return_value = mock_resp
    resp = spycloud.spycloud_ato_search("email", "test@example.com")
    assert resp == mock_resp
    mock_make_request.assert_called_once()


def test_spycloud_ato_search_invalid_type():
    with patch.object(spycloud, "env_config", {"SPYCLOUD_API_ATO_KEY": "fake"}):
        with pytest.raises(SystemExit):
            spycloud.spycloud_ato_search("invalid", "query")


@patch.object(spycloud, "env_config", {"SPYCLOUD_API_INV_KEY": "fake"})
@patch("ppp_connectors.connectors.spycloud.make_request")
def test_spycloud_inv_search_valid(mock_make_request):
    mock_resp = MagicMock()
    mock_make_request.return_value = mock_resp
    resp = spycloud.spycloud_inv_search("domain", "example.com")
    assert resp == mock_resp
    mock_make_request.assert_called_once()


def test_spycloud_inv_search_invalid_type():
    with patch.object(spycloud, "env_config", {"SPYCLOUD_API_INV_KEY": "fake"}):
        with pytest.raises(SystemExit):
            spycloud.spycloud_inv_search("invalid-type", "query")