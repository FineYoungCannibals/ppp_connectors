import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.generic import GenericConnector


def test_init_sets_base_url():
    connector = GenericConnector(base_url="https://example.com")
    assert connector.base_url == "https://example.com"


@patch("ppp_connectors.api_connectors.generic.GenericConnector._make_request")
def test_get_request(mock_make_request):
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "ok"}
    mock_make_request.return_value = mock_response

    connector = GenericConnector(base_url="https://example.com")
    response = connector.get("/test")

    assert response.json() == {"result": "ok"}
    mock_make_request.assert_called_once_with("GET", "/test", params=None)


@patch("ppp_connectors.api_connectors.generic.GenericConnector._make_request")
def test_post_request(mock_make_request):
    mock_response = MagicMock()
    mock_response.json.return_value = {"posted": True}
    mock_make_request.return_value = mock_response

    connector = GenericConnector(base_url="https://example.com")
    response = connector.post("/submit", json={"key": "value"})

    assert response.json() == {"posted": True}
    mock_make_request.assert_called_once_with("POST", "/submit", json={"key": "value"})
