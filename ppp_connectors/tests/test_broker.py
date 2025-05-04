import pytest
from unittest.mock import patch, MagicMock
from requests.auth import HTTPBasicAuth
from ppp_connectors import broker

BASE_URL = "https://api.example.com/resource"


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setattr(broker, "env_config", {
        "PPP_HTTP_PROXY": "http://proxy.local",
        "PPP_HTTPS_PROXY": "https://proxy.local",
        "VERIFY_SSL": "false"
    })


@pytest.fixture
def mock_check_env_vars(monkeypatch):
    monkeypatch.setattr(broker, "check_required_env_vars", lambda *args, **kwargs: None)


@patch("ppp_connectors.broker.requests.get")
def test_make_get_request(mock_get, mock_env, mock_check_env_vars):
    mock_response = MagicMock(status_code=200)
    mock_get.return_value = mock_response

    result = broker.make_request("GET", BASE_URL, params={"key": "val"})

    mock_get.assert_called_once_with(
        BASE_URL,
        headers=None,
        auth=None,
        params={"key": "val"},
        data=None,
        json=None,
        proxies={
            "http": "http://proxy.local",
            "https": "https://proxy.local"
        },
        verify=False,
        timeout=15
    )
    assert result.status_code == 200


@patch("ppp_connectors.broker.requests.post")
def test_make_post_with_json(mock_post, mock_env, mock_check_env_vars):
    mock_response = MagicMock(status_code=201)
    mock_post.return_value = mock_response

    result = broker.make_request("POST", BASE_URL, json={"foo": "bar"})

    mock_post.assert_called_once()
    assert result.status_code == 201


@patch("ppp_connectors.broker.requests.get")
def test_make_request_with_auth(mock_get, mock_env, mock_check_env_vars):
    mock_response = MagicMock(status_code=200)
    mock_get.return_value = mock_response

    auth = HTTPBasicAuth("user", "")
    result = broker.make_request("GET", BASE_URL, auth=auth)

    mock_get.assert_called_once()
    assert result.status_code == 200


def test_unsupported_method(mock_env, mock_check_env_vars):
    with pytest.raises(ValueError, match="Unsupported HTTP method: FOO"):
        broker.make_request("FOO", BASE_URL)