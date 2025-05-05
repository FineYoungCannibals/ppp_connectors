import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import flashpoint


def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"data": "test"}
    return mock


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_search_communities(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_search_communities("test_query")
    assert resp.status_code == 200
    assert resp.json() == {"data": "test"}
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_search_fraud(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_search_fraud("test_query")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_search_marketplaces(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_search_marketplaces("test_query")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_search_media(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_search_media("test_query")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_get_media_object(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_get_media_object("fake_id")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.flashpoint.check_required_env_vars")
@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={"FLASHPOINT_API_KEY": "fake_api_key"})
def test_get_media_image(mock_env, mock_check, mock_request):
    resp = flashpoint.flashpoint_get_media_image("fake_storage_uri")
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.flashpoint.combine_env_configs", return_value={})
def test_flashpoint_missing_api_key(mock_env):
    with pytest.raises(SystemExit):
        flashpoint.flashpoint_search_communities("fake query")