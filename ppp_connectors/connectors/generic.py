from typing import Dict, Any, Optional
from requests import Response
from ppp_connectors.broker import make_request


def generic_api_call(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    auth: Optional[Any] = None,
    timeout: int = 15,
    **kwargs
) -> Response:
    """
    Generic wrapper around the broker"s make_request function.

    This allows you to hit any arbitrary API endpoint without a dedicated connector.

    Example:
        generic_api_call(
            method="GET",
            url="https://api.example.com/v1/info",
            headers={"Authorization": f"Bearer {token}"}
        )

    Returns:
        Response object from requests
    """
    return make_request(
        method=method,
        url=url,
        headers=headers,
        auth=auth,
        params=params,
        data=data,
        json=json,
        timeout=timeout,
        **kwargs
    )
