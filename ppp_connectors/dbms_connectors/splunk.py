import httpx
from typing import Generator, Dict, Any, Optional
from ppp_connectors.helpers import setup_logger


class SplunkConnector:
    """
    A connector class for interacting with Splunk via its REST API.

    Provides methods for submitting search jobs and streaming paginated results.
    """
    def __init__(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scheme: str = "https",
        verify: bool = True,
        timeout: int = 30,
        logger: Optional[Any] = None
    ):
        """
        Initialize the SplunkConnector with connection details.

        Args:
            host (str): The Splunk server host.
            port (int): The Splunk management port.
            username (Optional[str]): Username for authentication. Defaults to None.
            password (Optional[str]): Password for authentication. Defaults to None.
            scheme (str): HTTP or HTTPS. Defaults to "https".
            verify (bool): Whether to verify SSL certificates. Defaults to True.
            timeout (int): Request timeout in seconds. Defaults to 30.
            logger (Optional[Any]): Logger instance. If provided, actions will be logged.
        """
        self.base_url = f"{scheme}://{host}:{port}"
        self.auth = (username, password)
        self.verify = verify
        self.timeout = timeout
        self.logger = logger or setup_logger(__name__)

        # Suppress InsecureRequestWarnings if the user sets verify=False
        if not self.verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _log(self, msg: str, level: str = "info"):
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

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

        Logs actions if logger is enabled.
        """
        # 1️⃣ Create job
        self._log(f"Submitting search job: {search}")
        data = {
            "search": search,
            "output_mode": "json",
            "count": count
        }
        if earliest_time:
            data["earliest_time"] = earliest_time
        if latest_time:
            data["latest_time"] = latest_time

        create_resp = httpx.post(
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
            self._log(f"Polling job {sid} status...")
            status_resp = httpx.get(
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
            self._log(f"Fetching results batch starting at offset {offset}")
            results_resp = httpx.get(
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
