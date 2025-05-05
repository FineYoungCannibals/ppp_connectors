from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import urlscan


def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"result": "success"}
    return mock


@patch("ppp_connectors.connectors.urlscan.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.urlscan.check_required_env_vars")
@patch("ppp_connectors.connectors.urlscan.combine_env_configs", return_value={"URLSCAN_API_KEY": "dummy_key"})
def test_urlscan_search(mock_env, mock_check, mock_request):
    resp = urlscan.urlscan_search("example.com")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.urlscan.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.urlscan.check_required_env_vars")
@patch("ppp_connectors.connectors.urlscan.combine_env_configs", return_value={"URLSCAN_API_KEY": "dummy_key"})
def test_urlscan_scan(mock_env, mock_check, mock_request):
    resp = urlscan.urlscan_scan("http://example.com")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.urlscan.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.urlscan.check_required_env_vars")
@patch("ppp_connectors.connectors.urlscan.combine_env_configs", return_value={"URLSCAN_API_KEY": "dummy_key"})
def test_urlscan_results(mock_env, mock_check, mock_request):
    resp = urlscan.urlscan_results("uuid-example")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.urlscan.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.urlscan.combine_env_configs", return_value={"URLSCAN_API_KEY": "dummy_key"})
def test_urlscan_get_dom(mock_env, mock_request):
    resp = urlscan.urlscan_get_dom("uuid-example")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.urlscan.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.urlscan.check_required_env_vars")
@patch("ppp_connectors.connectors.urlscan.combine_env_configs", return_value={"URLSCAN_API_KEY": "dummy_key"})
def test_urlscan_structure_search(mock_env, mock_check, mock_request):
    resp = urlscan.urlscan_structure_search("uuid-example")
    assert resp.status_code == 200
    mock_request.assert_called_once()
