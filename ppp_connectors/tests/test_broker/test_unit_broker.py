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

def test_env_only_proxy_from_dotenv(monkeypatch, mocker):
    # Simulate .env via env_config when load_env_vars=True
    mock_combine = mocker.patch(
        "ppp_connectors.api_connectors.broker.combine_env_configs",
        return_value={"HTTPS_PROXY": "http://env-proxy:8080"}
    )
    broker = Broker(base_url="https://example.com", load_env_vars=True, trust_env=False)
    assert broker.proxy == "http://env-proxy:8080"
    assert broker.mounts is None
    mock_combine.assert_called_once()

def test_env_only_proxy_from_osenv(monkeypatch):
    # Simulate OS env with trust_env=True
    monkeypatch.setenv("HTTPS_PROXY", "http://os-proxy:9090")
    broker = Broker(base_url="https://example.com", load_env_vars=False, trust_env=True)
    assert broker.proxy == "http://os-proxy:9090"
    assert broker.mounts is None

def test_env_per_scheme_mounts(monkeypatch):
    # Different HTTP and HTTPS proxies from env
    monkeypatch.setenv("HTTP_PROXY", "http://http-proxy:8000")
    monkeypatch.setenv("HTTPS_PROXY", "http://https-proxy:9000")
    broker = Broker(base_url="https://example.com", load_env_vars=False, trust_env=True)
    assert broker.proxy is None
    assert "http://" in broker.mounts and "https://" in broker.mounts

def test_priority_mounts_over_proxy(monkeypatch):
    # If mounts are provided, they win
    mounts = {"http://": object(), "https://": object()}
    broker = Broker(base_url="https://example.com", mounts=mounts, proxy="http://should-not-use:1111")
    assert broker.mounts == mounts
    assert broker.proxy == "http://should-not-use:1111"  # Stored but not used for session if mounts present

def test_priority_proxy_over_env(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://os-proxy:9999")
    broker = Broker(base_url="https://example.com", proxy="http://explicit-proxy:7777", trust_env=True)
    assert broker.proxy == "http://explicit-proxy:7777"

def test_no_proxy_when_nothing_set(monkeypatch):
    monkeypatch.delenv("ALL_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    broker = Broker(base_url="https://example.com", load_env_vars=False, trust_env=False)
    assert broker.proxy is None
    assert broker.mounts is None
