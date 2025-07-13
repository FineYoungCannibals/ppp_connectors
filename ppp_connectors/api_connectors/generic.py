from typing import Dict, Any, Optional
from ppp_connectors.api_connectors.broker import Broker
import httpx

class GenericConnector(Broker):
    """
    A flexible, minimal connector that allows sending arbitrary HTTP requests
    using the Broker infrastructure.
    """

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        auth: Optional[Any] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make an arbitrary HTTP request using Broker's request logic.

        Args:
            method (str): HTTP method (e.g., GET, POST).
            url (str): Fully qualified URL to send the request to.
            headers (Optional[Dict[str, str]]): Request headers.
            params (Optional[Dict[str, Any]]): Query string parameters.
            data (Optional[Any]): Form-encoded or raw data.
            json (Optional[Dict[str, Any]]): JSON payload.
            auth (Optional[Any]): Authentication (e.g., tuple for basic auth).
            timeout (Optional[int]): Request timeout in seconds.

        Returns:
            httpx.Response: The response object.
        """

        # Merge headers with base class
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)

        return self._make_request(
            method=method,
            endpoint=url,
            headers=merged_headers,
            params=params,
            json=json,
            auth=auth,
            retry_kwargs=kwargs.get("retry_kwargs"),
        )
