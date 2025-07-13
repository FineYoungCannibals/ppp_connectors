import pytest
from ppp_connectors.api_connectors.broker import Broker

def test_get_calls_make_request(mocker):
    broker = Broker(base_url="https://example.com")
    mock_request = mocker.patch.object(broker, "_make_request")
    broker.get("/test", params={"foo": "bar"})
    mock_request.assert_called_once_with("GET", "/test", params={"foo": "bar"})

def test_post_calls_make_request(mocker):
    broker = Broker(base_url="https://example.com")
    mock_request = mocker.patch.object(broker, "_make_request")
    broker.post("/submit", json={"data": 123})
    mock_request.assert_called_once_with("POST", "/submit", json={"data": 123})

def test_logging_enabled_logs_message(mocker):
    mock_logger = mocker.MagicMock()
    mock_setup_logger = mocker.patch("ppp_connectors.api_connectors.broker.setup_logger", return_value=mock_logger)
    broker = Broker(base_url="https://example.com", enable_logging=True)
    broker._log("test message")
    mock_logger.info.assert_called_once_with("test message")
