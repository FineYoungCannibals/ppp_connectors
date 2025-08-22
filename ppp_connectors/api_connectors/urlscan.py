import httpx
from typing import Dict, Any, Optional
from ppp_connectors.api_connectors.broker import AsyncBroker, Broker, bubble_broker_init_signature, log_method_call

@bubble_broker_init_signature()
class URLScanConnector(Broker):
    """
    A connector for interacting with the urlscan.io API.

    Provides structured methods for submitting scans, querying historical data,
    and retrieving detailed scan results and metadata.

    Attributes:
        api_key (str): The API key used to authenticate with urlscan.io.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://urlscan.io", **kwargs)

        self.api_key = api_key or self.env_config.get("URLSCAN_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for URLScanConnector")
        self.headers.update({
            "accept": "application/json",
            "API-Key": self.api_key
        })

    @log_method_call
    def search(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Search for archived scans matching a given query.

        Args:
            query (str): The search term or filter string.
            **kwargs: Additional query parameters for filtering results.

        Returns:
            httpx.Response: the httpx.Response object
        """
        params = {"q": query, **kwargs}
        return self.get("/api/v1/search/", params=params)

    @log_method_call
    def scan(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Submit a URL to be scanned by urlscan.io.

        Args:
            query (str): The URL to scan.
            **kwargs: Additional scan options like tags, visibility, or referer.

        Returns:
            httpx.Response: the httpx.Response object
        """
        payload = {"url": query, **kwargs}
        return self.post("/api/v1/scan", json=payload)

    @log_method_call
    def results(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Retrieve detailed scan results by UUID.

        Args:
            query (str): The UUID of the scan.

        Returns:
            httpx.Response: the httpx.Response object
        """
        return self.get(f"/api/v1/result/{query}", params=kwargs)

    @log_method_call
    def get_dom(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Retrieve the DOM snapshot for a given scan UUID.

        Args:
            query (str): The UUID of the scan.

        Returns:
            httpx.Response: the httpx.Response object
        """
        return self.get(f"/dom/{query}", params=kwargs)

    @log_method_call
    def structure_search(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Search for scans structurally similar to a given UUID.

        Args:
            query (str): The UUID of the original scan.

        Returns:
            httpx.Response: the httpx.Response object
        """
        return self.get(f"/api/v1/pro/result/{query}/similar", params=kwargs)

class AsyncURLScanConnector(AsyncBroker):
    """
    An async connector for interacting with the urlscan.io API.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://urlscan.io", **kwargs)

        self.api_key = api_key or self.env_config.get("URLSCAN_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for AsyncURLScanConnector")
        self.headers.update({
            "accept": "application/json",
            "API-Key": self.api_key
        })

    @log_method_call
    async def search(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Async search for archived scans matching a given query.
        """
        params = {"q": query, **kwargs}
        return await self.get("/api/v1/search/", params=params)

    @log_method_call
    async def scan(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Async submit a URL to be scanned by urlscan.io.
        """
        payload = {"url": query, **kwargs}
        return await self.post("/api/v1/scan", json=payload)

    @log_method_call
    async def results(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Async retrieve detailed scan results by UUID.
        """
        return await self.get(f"/api/v1/result/{query}", params=kwargs)

    @log_method_call
    async def get_dom(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Async retrieve the DOM snapshot for a given scan UUID.
        """
        return await self.get(f"/dom/{query}", params=kwargs)

    @log_method_call
    async def structure_search(self, query: str, **kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Async search for scans structurally similar to a given UUID.
        """
        return await self.get(f"/api/v1/pro/result/{query}/similar", params=kwargs)
