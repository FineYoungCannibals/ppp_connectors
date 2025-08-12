import httpx
import pytest
from ppp_connectors.api_connectors.urlscan import URLScanConnector

@pytest.mark.integration
def test_urlscan_results_vcr(vcr_cassette):
    with vcr_cassette.use_cassette("test_urlscan_results_vcr"):
        connector = URLScanConnector(load_env_vars=True, enable_logging=True)
        result = connector.results("01958568-c986-7001-816d-9e0ccd7c4c4a")

        assert isinstance(result, httpx.Response)
        assert "task" in result.json()