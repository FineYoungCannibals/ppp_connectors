import httpx
import pytest
from ppp_connectors.api_connectors.spycloud import SpycloudConnector

@pytest.mark.integration
def test_spycloud_ato_search_vcr(vcr_cassette):
    with vcr_cassette.use_cassette("test_spycloud_ato_search_vcr"):
        connector = SpycloudConnector(load_env_vars=True, enable_logging=True)
        result = connector.ato_search(search_type="ip", query="8.8.8.8")

        assert isinstance(result, httpx.Response)
        assert "results" in result.json()