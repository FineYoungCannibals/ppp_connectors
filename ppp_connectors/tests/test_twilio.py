import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import twilio


def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"valid": True}
    return mock


@patch("ppp_connectors.connectors.twilio.make_request", return_value=mock_response())
@patch("ppp_connectors.connectors.twilio.check_required_env_vars")
@patch("ppp_connectors.connectors.twilio.combine_env_configs", return_value={
    "TWILIO_API_SID": "fake_sid",
    "TWILIO_API_SECRET": "fake_token",
    "TWILIO_ACCOUNT_SID": "fake_sid"
})
def test_twilio_lookup_phone_number(mock_env, mock_check, mock_request):
    resp = twilio.twilio_lookup("+14155552671", ["line_status"])
    assert resp.status_code == 200
    mock_request.assert_called_once()


@patch("ppp_connectors.connectors.twilio.combine_env_configs", return_value={})
def test_twilio_lookup_phone_number_missing_env(mock_env):
    with pytest.raises(SystemExit):
        twilio.twilio_lookup("+14155552671")