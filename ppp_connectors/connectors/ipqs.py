from typing import Dict, Any, List
from requests import Response
from urllib.parse import quote
from ppp_connectors.broker import make_request
from ppp_connectors.helpers import check_required_env_vars, combine_env_configs


def ipqs_malicious_url(query: str, **kwargs: Dict[str, Any]) -> Response:
    """IPQualityScore's Malicious URL Scanner API scans links in real-time
        to detect suspicious URLs. Accurately identify phishing links, malware
        URLs and viruses, parked domains, and suspicious URLs with real-time risk
        scores. Industry leading phishing detection and domain reputation provide
        better signals for more accurate decision making.

    Args:
        query (str): The URL to scan

    Returns:
        Response: requests.Response json response from the request
    """

    env_config: Dict[str, Any] = combine_env_configs()

    # Define required environment variables
    required_vars: List[str] = [
        'IPQS_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'post'
    url: str = 'https://ipqualityscore.com/api/json/url'
    headers: Dict = {'accept': 'application/json'}
    encoded_query: str = quote(query)
    params: Dict = {
        'key': env_config['IPQS_API_KEY'],
        'url': encoded_query,
        **kwargs
    }

    result: Response = make_request(
        method=method,
        url=url,
        headers=headers,
        json=params,
        timeout=kwargs.get("timeout")
    )

    return result
