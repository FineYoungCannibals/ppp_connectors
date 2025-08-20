from datetime import date, datetime
from typing import Dict, Any, List, Set, Union, Optional
from httpx import BasicAuth, Response
from ppp_connectors.api_connectors.broker import AsyncBroker, Broker, bubble_broker_init_signature, log_method_call
from ppp_connectors.helpers import validate_date_string

@bubble_broker_init_signature()
class TwilioConnector(Broker):
    """
    Connector for interacting with Twilio Lookup and Usage APIs.

    Supports phone number lookups with data packages and generating account usage reports.
    """

    def __init__(
        self,
        api_sid: Optional[str] = None,
        api_secret: Optional[str] = None,
        **kwargs
    ):
        super().__init__(base_url="https://lookups.twilio.com/v2", **kwargs)

        self.api_sid = api_sid or self.env_config.get("TWILIO_API_SID")
        self.api_secret = api_secret or self.env_config.get("TWILIO_API_SECRET")

        if not self.api_sid or not self.api_secret:
            raise ValueError("TWILIO_API_SID and TWILIO_API_SECRET are required.")

        self.auth = BasicAuth(self.api_sid, self.api_secret)

    @log_method_call
    def lookup_phone(self, phone_number: str, data_packages: Optional[List[str]] = None, **kwargs) -> Response:
        """
        Query information about a phone number using Twilio's Lookup API.

        Args:
            phone_number (str): The phone number to query.
            data_packages (list): Optional data packages to include (e.g. 'caller_name', 'sim_swap').

        Returns:
            httpx.Response: the httpx.Response object
        """
        valid_data_packages: Set[str] = {
            'caller_name', 'sim_swap', 'call_forwarding', 'line_status',
            'line_type_intelligence', 'identity_match', 'reassigned_number',
            'sms_pumping_risk', 'phone_number_quality_score', 'pre_fill'
        }

        if data_packages:
            invalid = set(data_packages) - valid_data_packages
            if invalid:
                raise ValueError(f"Invalid data packages: {', '.join(invalid)}")

        params: Dict[str, Any] = {
            'Fields': ','.join(data_packages) if data_packages else "",
            **kwargs
        }

        endpoint = f"/PhoneNumbers/{phone_number}"
        return self._make_request("get", endpoint=endpoint, auth=self.auth, params=params)


@bubble_broker_init_signature()
class AsyncTwilioConnector(AsyncBroker):
    """
    Async connector for interacting with Twilio Lookup API.
    """

    def __init__(
        self,
        api_sid: Optional[str] = None,
        api_secret: Optional[str] = None,
        **kwargs
    ):
        super().__init__(base_url="https://lookups.twilio.com/v2", **kwargs)

        self.api_sid = api_sid or self.env_config.get("TWILIO_API_SID")
        self.api_secret = api_secret or self.env_config.get("TWILIO_API_SECRET")

        if not self.api_sid or not self.api_secret:
            raise ValueError("TWILIO_API_SID and TWILIO_API_SECRET are required.")

        self.auth = BasicAuth(self.api_sid, self.api_secret)

    @log_method_call
    async def lookup_phone(self, phone_number: str, data_packages: Optional[List[str]] = None, **kwargs) -> Response:
        """
        Async version of phone number lookup using Twilio Lookup API.

        Args:
            phone_number (str): The phone number to query.
            data_packages (list): Optional data packages to include (e.g. 'caller_name', 'sim_swap').

        Returns:
            httpx.Response: the httpx.Response object
        """
        valid_data_packages: Set[str] = {
            'caller_name', 'sim_swap', 'call_forwarding', 'line_status',
            'line_type_intelligence', 'identity_match', 'reassigned_number',
            'sms_pumping_risk', 'phone_number_quality_score', 'pre_fill'
        }

        if data_packages:
            invalid = set(data_packages) - valid_data_packages
            if invalid:
                raise ValueError(f"Invalid data packages: {', '.join(invalid)}")

        params: Dict[str, Any] = {
            'Fields': ','.join(data_packages) if data_packages else "",
            **kwargs
        }

        endpoint = f"/PhoneNumbers/{phone_number}"
        return await self._make_request("get", endpoint=endpoint, auth=self.auth, params=params)