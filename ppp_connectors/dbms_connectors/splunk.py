import requests
from typing import Generator, Dict, Any, Optional


class SplunkConnector:
    """
    A connector class for interacting with Splunk via its REST API.

    Provides methods for submitting search jobs and streaming paginated results.
    """
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        scheme: str = "https",
        verify: bool = True,
        timeout: int = 30
    ):
        """
        Initialize the SplunkConnector with connection details.

        Args:
            host (str): The Splunk server host.
            port (int): The Splunk management port.
            username (str): Username for authentication.
            password (str): Password for authentication.
            scheme (str): HTTP or HTTPS. Defaults to "https".
            verify (bool): Whether to verify SSL certificates. Defaults to True.
            timeout (int): Request timeout in seconds. Defaults to 30.
        """
        self.base_url = f"{scheme}://{host}:{port}"
        self.auth = (username, password)
        self.verify = verify
        self.timeout = timeout

    def query(
        self,
        search: str,
        count: int = 1000,
        earliest_time: Optional[str] = None,
        latest_time: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Submit a search job to Splunk and stream results as dictionaries.

        Args:
            search (str): The search query string.
            count (int): Number of results per batch. Defaults to 1000.
            earliest_time (Optional[str]): Earliest time for the search. Defaults to None.
            latest_time (Optional[str]): Latest time for the search. Defaults to None.

        Yields:
            Dict[str, Any]: Each search result as a dictionary.
        """
        # 1️⃣ Create job
        data = {
            "search": search,
            "output_mode": "json",
            "count": count
        }
        if earliest_time:
            data["earliest_time"] = earliest_time
        if latest_time:
            data["latest_time"] = latest_time

        create_resp = requests.post(
            f"{self.base_url}/services/search/jobs",
            auth=self.auth,
            data=data,
            verify=self.verify,
            timeout=self.timeout
        )
        create_resp.raise_for_status()
        sid = create_resp.json()["sid"]

        # 2️⃣ Poll until ready
        while True:
            status_resp = requests.get(
                f"{self.base_url}/services/search/jobs/{sid}",
                auth=self.auth,
                params={"output_mode": "json"},
                verify=self.verify,
                timeout=self.timeout
            )
            status_resp.raise_for_status()
            content = status_resp.json()
            if content["entry"][0]["content"]["isDone"]:
                break

        # 3️⃣ Fetch results
        offset = 0
        while True:
            results_resp = requests.get(
                f"{self.base_url}/services/search/jobs/{sid}/results",
                auth=self.auth,
                params={
                    "output_mode": "json",
                    "count": count,
                    "offset": offset
                },
                verify=self.verify,
                timeout=self.timeout
            )
            results_resp.raise_for_status()
            results = results_resp.json().get("results", [])
            if not results:
                break
            for row in results:
                yield row
            offset += len(results)
