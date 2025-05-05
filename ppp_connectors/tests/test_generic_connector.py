import pytest
from unittest.mock import patch, MagicMock
from requests.auth import HTTPBasicAuth
from ppp_connectors.connectors.generic import generic_api_call


@patch("ppp_connectors.connectors.generic.make_request")
def test_generic_api_call_get(mock_make_request):
    mock_response = MagicMock(status_code=200)
    mock_make_request.return_value = mock_response

    resp = generic_api_call(method="GET", url="https://example.com")

    mock_make_request.assert_called_once_with(
        method="GET",
        url="https://example.com",
        headers=None,
        auth=None,
        params=None,
        data=None,
        json=None,
        timeout=15
    )
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.generic.make_request")
def test_generic_api_call_post_with_json(mock_make_request):
    mock_response = MagicMock(status_code=201)
    mock_make_request.return_value = mock_response

    body = {"foo": "bar"}
    resp = generic_api_call(method="POST", url="https://example.com", json=body)

    mock_make_request.assert_called_once_with(
        method="POST",
        url="https://example.com",
        headers=None,
        auth=None,
        params=None,
        data=None,
        json=body,
        timeout=15
    )
    assert resp.status_code == 201


@patch("ppp_connectors.connectors.generic.make_request")
def test_generic_api_call_with_auth(mock_make_request):
    mock_response = MagicMock(status_code=200)
    mock_make_request.return_value = mock_response

    auth = HTTPBasicAuth("user", "")
    resp = generic_api_call(method="GET", url="https://example.com", auth=auth)

    mock_make_request.assert_called_once()
    assert resp.status_code == 200


@patch("ppp_connectors.connectors.generic.make_request")
def test_generic_api_call_with_extra_kwargs(mock_make_request):
    mock_response = MagicMock(status_code=200)
    mock_make_request.return_value = mock_response

    resp = generic_api_call(method="GET", url="https://example.com", timeout=30, custom="value")

    mock_make_request.assert_called_once_with(
        method="GET",
        url="https://example.com",
        headers=None,
        auth=None,
        params=None,
        data=None,
        json=None,
        timeout=30,
        custom="value"
    )
    assert resp.status_code == 200
