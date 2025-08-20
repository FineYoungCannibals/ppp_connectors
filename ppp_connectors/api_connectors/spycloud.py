import httpx
from typing import Dict, Any, Optional
from ppp_connectors.api_connectors.broker import AsyncBroker, Broker, bubble_broker_init_signature, log_method_call


@bubble_broker_init_signature()
class SpycloudConnector(Broker):
    """
    SpyCloudConnector provides typed methods to interact with various SpyCloud APIs, including:
    - SIP Cookie Domains
    - ATO Breach Catalog
    - ATO Search
    - Investigations Search
    """

    def __init__(self, sip_key: Optional[str] = None, ato_key: Optional[str] = None,
                 inv_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.spycloud.io", **kwargs)
        self.sip_key = sip_key or self.env_config.get("SPYCLOUD_API_SIP_KEY")
        self.ato_key = ato_key or self.env_config.get("SPYCLOUD_API_ATO_KEY")
        self.inv_key = inv_key or self.env_config.get("SPYCLOUD_API_INV_KEY")

    @log_method_call
    def sip_cookie_domains(self, cookie_domains: str, **kwargs) -> httpx.Response:
        """Query SIP cookie domain data."""
        if not self.sip_key:
            raise ValueError("SPYCLOUD_API_SIP_KEY is required for this request.")
        endpoint = f"/sip-v1/breach/data/cookie-domains/{cookie_domains}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.sip_key
        }
        return self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)

    @log_method_call
    def ato_breach_catalog(self, query: str, **kwargs) -> httpx.Response:
        """Query ATO breach catalog."""
        if not self.ato_key:
            raise ValueError("SPYCLOUD_API_ATO_KEY is required for this request.")
        endpoint = "/sp-v2/breach/catalog"
        headers = {
            "accept": "application/json",
            "x-api-key": self.ato_key
        }
        params = {"query": query, **kwargs}
        return self._make_request("get", endpoint=endpoint, headers=headers, params=params)

    @log_method_call
    def ato_search(self, search_type: str, query: str, **kwargs) -> httpx.Response:
        """Search against SpyCloud's ATO breach dataset."""
        if not self.ato_key:
            raise ValueError("SPYCLOUD_API_ATO_KEY is required for this request.")

        base_url = "/sp-v2/breach/data"
        endpoints = {
            'domain': 'domains',
            'email': 'emails',
            'ip': 'ips',
            'username': 'usernames',
            'phone-number': 'phone-numbers',
        }

        if search_type not in endpoints:
            raise ValueError(f'Invalid search_type: {search_type}. Must be one of: {", ".join(endpoints.keys())}')

        endpoint = f"{base_url}/{endpoints[search_type]}/{query}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.ato_key
        }
        return self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)

    @log_method_call
    def investigations_search(self, search_type: str, query: str, **kwargs) -> httpx.Response:
        """Search SpyCloud Investigations API by type and query."""
        if not self.inv_key:
            raise ValueError("SPYCLOUD_API_INV_KEY is required for this request.")

        base_url = "/investigations-v2/breach/data"
        endpoints = {
            'domain': 'domains',
            'email': 'emails',
            'ip': 'ips',
            'infected-machine-id': 'infected-machine-ids',
            'log-id': 'log-ids',
            'password': 'passwords',
            'username': 'usernames',
            'email-username': 'email-usernames',
            'phone-number': 'phone-numbers',
            'social-handle': 'social-handles',
            'bank-number': 'bank-numbers',
            'cc-number': 'cc-numbers',
            'drivers-license': 'drivers-licenses',
            'national-id': 'national-ids',
            'passport-number': 'passport-numbers',
            'ssn': 'social-security-numbers',
        }

        if search_type not in endpoints:
            raise ValueError(f'Invalid search_type: {search_type}. Must be one of: {", ".join(endpoints.keys())}')

        endpoint = f"{base_url}/{endpoints[search_type]}/{query}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.inv_key
        }
        return self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)


@bubble_broker_init_signature()
class AsyncSpycloudConnector(AsyncBroker):
    """
    Async version of SpycloudConnector.
    """

    def __init__(self, sip_key: Optional[str] = None, ato_key: Optional[str] = None,
                 inv_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.spycloud.io", **kwargs)
        self.sip_key = sip_key or self.env_config.get("SPYCLOUD_API_SIP_KEY")
        self.ato_key = ato_key or self.env_config.get("SPYCLOUD_API_ATO_KEY")
        self.inv_key = inv_key or self.env_config.get("SPYCLOUD_API_INV_KEY")

    @log_method_call
    async def sip_cookie_domains(self, cookie_domains: str, **kwargs) -> httpx.Response:
        """Query SIP cookie domain data (async)."""
        if not self.sip_key:
            raise ValueError("SPYCLOUD_API_SIP_KEY is required for this request.")
        endpoint = f"/sip-v1/breach/data/cookie-domains/{cookie_domains}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.sip_key
        }
        return await self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)

    @log_method_call
    async def ato_breach_catalog(self, query: str, **kwargs) -> httpx.Response:
        """Query ATO breach catalog (async)."""
        if not self.ato_key:
            raise ValueError("SPYCLOUD_API_ATO_KEY is required for this request.")
        endpoint = "/sp-v2/breach/catalog"
        headers = {
            "accept": "application/json",
            "x-api-key": self.ato_key
        }
        params = {"query": query, **kwargs}
        return await self._make_request("get", endpoint=endpoint, headers=headers, params=params)

    @log_method_call
    async def ato_search(self, search_type: str, query: str, **kwargs) -> httpx.Response:
        """Search against SpyCloud's ATO breach dataset (async)."""
        if not self.ato_key:
            raise ValueError("SPYCLOUD_API_ATO_KEY is required for this request.")

        base_url = "/sp-v2/breach/data"
        endpoints = {
            'domain': 'domains',
            'email': 'emails',
            'ip': 'ips',
            'username': 'usernames',
            'phone-number': 'phone-numbers',
        }

        if search_type not in endpoints:
            raise ValueError(f'Invalid search_type: {search_type}. Must be one of: {", ".join(endpoints.keys())}')

        endpoint = f"{base_url}/{endpoints[search_type]}/{query}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.ato_key
        }
        return await self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)

    @log_method_call
    async def investigations_search(self, search_type: str, query: str, **kwargs) -> httpx.Response:
        """Search SpyCloud Investigations API by type and query (async)."""
        if not self.inv_key:
            raise ValueError("SPYCLOUD_API_INV_KEY is required for this request.")

        base_url = "/investigations-v2/breach/data"
        endpoints = {
            'domain': 'domains',
            'email': 'emails',
            'ip': 'ips',
            'infected-machine-id': 'infected-machine-ids',
            'log-id': 'log-ids',
            'password': 'passwords',
            'username': 'usernames',
            'email-username': 'email-usernames',
            'phone-number': 'phone-numbers',
            'social-handle': 'social-handles',
            'bank-number': 'bank-numbers',
            'cc-number': 'cc-numbers',
            'drivers-license': 'drivers-licenses',
            'national-id': 'national-ids',
            'passport-number': 'passport-numbers',
            'ssn': 'social-security-numbers',
        }

        if search_type not in endpoints:
            raise ValueError(f'Invalid search_type: {search_type}. Must be one of: {", ".join(endpoints.keys())}')

        endpoint = f"{base_url}/{endpoints[search_type]}/{query}"
        headers = {
            "accept": "application/json",
            "x-api-key": self.inv_key
        }
        return await self._make_request("get", endpoint=endpoint, headers=headers, params=kwargs)