from typing import Dict, Any, Optional
from ppp_connectors.api_connectors.broker import Broker

"""
URLScan Connector

This module provides a typed connector for the urlscan.io API, built on the Broker class.
It supports searching, scanning, and retrieving structured results for analyzed URLs.
"""

class URLScanConnector(Broker):
    """
    A connector for interacting with the urlscan.io API.

    Provides structured methods for submitting scans, querying historical data,
    and retrieving detailed scan results and metadata.

    Attributes:
        api_key (str): The API key used to authenticate with urlscan.io.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://urlscan.io/api/v1", **kwargs)

        self.api_key = api_key or self.env_config.get("URLSCAN_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for URLScanConnector")
        self.headers.update({
            "accept": "application/json",
            "API-Key": self.api_key
        })

    def search(self, query: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for archived scans matching a given query.

        Args:
            query (str): The search term or filter string.
            **kwargs: Additional query parameters for filtering results.

        Returns:
            dict: JSON response with matching scan metadata.
        """
        params = {"q": query, **kwargs}
        return self.get("/search/", params=params).json()

    def scan(self, query: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a URL to be scanned by urlscan.io.

        Args:
            query (str): The URL to scan.
            **kwargs: Additional scan options like tags, visibility, or referer.

        Returns:
            dict: JSON response containing the scan ID and status.
        """
        payload = {"url": query, **kwargs}
        return self.post("/scan", json=payload).json()

    def results(self, uuid: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve detailed scan results by UUID.

        Args:
            uuid (str): The UUID of the scan.

        Returns:
            dict: JSON response with scan results and metadata.
        """
        return self.get(f"/result/{uuid}", params=kwargs).json()

    def get_dom(self, uuid: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve the DOM snapshot for a given scan UUID.

        Args:
            uuid (str): The UUID of the scan.

        Returns:
            dict: JSON response with the scanned DOM content.
        """
        return self.get(f"https://urlscan.io/dom/{uuid}", params=kwargs).json()

    def structure_search(self, uuid: str, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for scans structurally similar to a given UUID.

        Args:
            uuid (str): The UUID of the original scan.

        Returns:
            dict: JSON response with similar scan entries.
        """
        return self.get(f"/pro/result/{uuid}/similar", params=kwargs).json()
