import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.api_connectors.twilio import TwilioConnector


def test_init_with_all_keys():
    connector = TwilioConnector(api_sid="sid", api_secret="secret")
    assert connector.api_sid == "sid"
    assert connector.auth is not None


@patch.dict("os.environ", {"TWILIO_API_SID": "sid", "TWILIO_API_SECRET": "secret"}, clear=True)
def test_init_with_env_keys():
    connector = TwilioConnector(load_env_vars=True)
    assert connector.api_sid == "sid"
    assert connector.auth is not None


@patch("ppp_connectors.api_connectors.broker.combine_env_configs", return_value={})
def test_init_missing_auth_keys(mock_env):
    with pytest.raises(ValueError, match="TWILIO_API_SID and TWILIO_API_SECRET are required"):
        TwilioConnector(load_env_vars=True)


@patch("ppp_connectors.api_connectors.twilio.TwilioConnector._make_request")
def test_lookup_phone(mock_request):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"carrier": "example"}
    mock_request.return_value = mock_resp

    connector = TwilioConnector(api_sid="sid", api_secret="secret")
    result = connector.lookup_phone("+15555555555")

    assert "carrier" in result
    mock_request.assert_called_once()