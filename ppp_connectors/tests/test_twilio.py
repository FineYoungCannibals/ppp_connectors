import pytest
from unittest.mock import patch, MagicMock
from ppp_connectors.connectors import twilio


@patch.object(twilio, "env_config", {"TWILIO_API_SID": "fake_sid", "TWILIO_API_SECRET": "fake_token"})
@patch("ppp_connectors.connectors.twilio.make_request")
def test_twilio_lookup_phone_number(mock_make_request):
    mock_resp = MagicMock()
    mock_make_request.return_value = mock_resp
    resp = twilio.twilio_lookup("+14155552671", ["line_status"])
    assert resp == mock_resp
    mock_make_request.assert_called_once()


def test_twilio_lookup_phone_number_missing_env():
    with patch.object(twilio, "env_config", {}):
        with pytest.raises(SystemExit):
            twilio.twilio_lookup("+14155552671")
