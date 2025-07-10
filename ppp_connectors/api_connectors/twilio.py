from datetime import date, datetime
from typing import Dict, Any, List, Set, Union, Optional
from httpx import BasicAuth
from ppp_connectors.api_connectors.broker import Broker
from ppp_connectors.helpers import validate_date_string

class TwilioConnector(Broker):
    """
    Connector for interacting with Twilio Lookup and Usage APIs.

    Supports phone number lookups with data packages and generating account usage reports.
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        api_sid: Optional[str] = None,
        api_secret: Optional[str] = None,
        **kwargs
    ):
        super().__init__(base_url="", **kwargs)

        self.account_sid = account_sid or self.env_config.get("TWILIO_ACCOUNT_SID")
        self.api_sid = api_sid or self.env_config.get("TWILIO_API_SID")
        self.api_secret = api_secret or self.env_config.get("TWILIO_API_SECRET")

        if not self.api_sid or not self.api_secret:
            raise ValueError("TWILIO_API_SID and TWILIO_API_SECRET are required.")

        self.auth = BasicAuth(self.api_sid, self.api_secret)

    def lookup_phone(self, phone_number: str, data_packages: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Query information about a phone number using Twilio's Lookup API.

        Args:
            phone_number (str): The phone number to query.
            data_packages (list): Optional data packages to include (e.g. 'caller_name', 'sim_swap').

        Returns:
            dict: JSON response from Twilio.
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

        url = f"https://lookups.twilio.com/v2/PhoneNumbers/{phone_number}"
        return self._make_request("get", endpoint=url, auth=self.auth, params=params).json()

    def usage_report(self, start_date: Union[str, date], end_date: Optional[Union[str, date]] = None) -> Dict[str, Any]:
        """
        Generate a usage report from Twilio's Usage API.

        Args:
            start_date (str or date): Start date in YYYY-MM-DD format.
            end_date (str or date, optional): End date in YYYY-MM-DD format. Defaults to today.

        Returns:
            dict: JSON usage report.
        """
        if not self.account_sid:
            raise ValueError("TWILIO_ACCOUNT_SID is required to generate usage reports.")

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        if not validate_date_string(start_date) or not validate_date_string(end_date):
            raise ValueError("Start or end date is not in YYYY-MM-DD format")

        params = {
            "StartDate": str(start_date),
            "EndDate": str(end_date)
        }

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Usage/Records.json"
        return self._make_request("get", endpoint=url, auth=self.auth, params=params).json()
