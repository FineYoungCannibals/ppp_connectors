import requests
from typing import Generator, Dict, Any, Optional


class SplunkConnector:
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
        Submit a search job and stream results.
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
