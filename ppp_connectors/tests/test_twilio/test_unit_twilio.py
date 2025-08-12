import httpx
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
    import json
    # Return a real httpx.Response to reflect new return type
    req = httpx.Request("GET", "https://lookups.twilio.com/v2/PhoneNumbers/15555555555")
    payload = {"carrier": "example"}
    resp = httpx.Response(
        200,
        request=req,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_request.return_value = resp

    connector = TwilioConnector(api_sid="sid", api_secret="secret")
    result = connector.lookup_phone("15555555555")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_request.assert_called_once()