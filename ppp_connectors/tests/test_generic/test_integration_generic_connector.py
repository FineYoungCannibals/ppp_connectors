import pytest
import vcr
from ppp_connectors.api_connectors.generic import GenericConnector

@pytest.mark.integration
def test_generic_get_github_api(vcr_cassette):
    with vcr_cassette.use_cassette("test_generic_get_github_api"):
        connector = GenericConnector(base_url="https://api.github.com")
        response = connector.get("/")

        data = response.json()
        assert "current_user_url" in data
