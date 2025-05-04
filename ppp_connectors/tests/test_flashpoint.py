import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import flashpoint


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setitem(flashpoint.env_config, 'FLASHPOINT_API_KEY', 'fake_api_key')


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"data": "test"}
    return mock


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_search_communities(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_search_communities("test_query")
    assert resp.status_code == 200
    assert resp.json() == {"data": "test"}


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_search_fraud(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_search_fraud("test_query")
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_search_marketplaces(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_search_marketplaces("test_query")
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_search_media(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_search_media("test_query")
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_get_media_object(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_get_media_object("fake_id")
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.flashpoint.make_request")
def test_get_media_image(mock_make_request, mock_env, mock_response):
    mock_make_request.return_value = mock_response
    resp = flashpoint.flashpoint_get_media_image("fake_storage_uri")
    assert resp.status_code == 200


def test_flashpoint_missing_api_key():
    with patch.object(flashpoint, "env_config", {}):
        with pytest.raises(SystemExit):
            flashpoint.flashpoint_search_communities("fake query")