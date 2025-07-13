"""
IPQS Connector

This module provides a connector for IPQualityScore's Malicious URL Scanner API.
The connector uses the shared Broker base class for HTTP operations, logging,
and environment variable loading.
"""
from typing import Optional, Dict, Any
from urllib.parse import quote
from ppp_connectors.api_connectors.broker import Broker, log_method_call


class IPQSConnector(Broker):
    """
    A connector for the IPQualityScore Malicious URL Scanner API.

    This class provides a typed interface to interact with IPQS's malicious URL
    scan endpoint. It handles API key management, header setup, and request routing
    through the shared Broker infrastructure.

    Attributes:
        api_key (str): The API key used to authenticate with IPQS.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://ipqualityscore.com/api/json", **kwargs)

        self.api_key = api_key or self.env_config.get("IPQS_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for IPQSConnector")
        self.headers.update({"Content-Type": "application/json"})

    @log_method_call
    def malicious_url(self, query: str, **kwargs) -> dict:
        """
        Scan a URL using IPQualityScore's Malicious URL Scanner API.

        Args:
            query (str): The URL to scan (will be URL-encoded).
            **kwargs: Optional parameters like 'strictness' or 'fast' to influence scan behavior.

        Returns:
            dict: Parsed JSON response from the IPQS API.
        """
        encoded_query: str = quote(query, safe="")
        return self.post(f"/url/", json={"url": query, "key": self.api_key, **kwargs}).json()
