
import httpx
import pytest
import vcr
from ppp_connectors.api_connectors.twilio import TwilioConnector

@pytest.mark.integration
def test_lookup_phone_vcr(vcr_cassette):
    with vcr_cassette.use_cassette("test_lookup_phone_vcr"):
        connector = TwilioConnector(load_env_vars=True)
        result = connector.lookup_phone("+14155552671")

        assert isinstance(result, httpx.Response)
        assert "phone_number" in result.json() or "caller_name" in result.json() or "line_type" in result.json()