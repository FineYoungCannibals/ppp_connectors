import pytest
import httpx
from ppp_connectors.api_connectors.broker import AsyncBroker


def test_asyncbroker_rejects_mounts():
    """Ensure that AsyncBroker raises an error if 'mounts' is passed."""
    with pytest.raises(ValueError, match="mounts.*not supported"):
        AsyncBroker(base_url="https://example.com", mounts={"http://": object()})


def test_asyncbroker_explicit_proxy_used(mocker):
    """Ensure that an explicitly provided proxy is passed to the AsyncClient."""
    client_mock = mocker.patch("httpx.AsyncClient")
    AsyncBroker(base_url="https://example.com", proxy="http://explicit:1234")
    client_mock.assert_called_once()
    assert client_mock.call_args.kwargs["proxy"] == "http://explicit:1234"