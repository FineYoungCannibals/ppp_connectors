import httpx
import pytest
from ppp_connectors.api_connectors.flashpoint import FlashpointConnector

@pytest.mark.integration
def test_flashpoint_search_fraud_vcr(vcr_cassette):
    with vcr_cassette.use_cassette("test_flashpoint_search_fraud_vcr"):
        connector = FlashpointConnector(load_env_vars=True)
        result = connector.search_fraud("dark web")
        assert isinstance(result, httpx.Response)
        assert "items" in result.json()