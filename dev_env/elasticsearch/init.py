import requests
from requests.auth import HTTPBasicAuth
import time
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
print(f'env = {os.getenv("ES_HOST")}')


def wait_for_es(url: str, timeout=60):
    for _ in range(timeout):
        try:
            r = requests.get(url, auth=HTTPBasicAuth(os.getenv("ES_USER"), os.getenv("ES_PASS")))
            if r.status_code == 200:
                return True
        except Exception:
            print("ES host is not yet available")
        time.sleep(1)
    raise TimeoutError("Elasticsearch did not become available.")


wait_for_es("http://elasticsearch:9200")

# Example index creation
resp = requests.put(
    "http://elasticsearch:9200/test-index",
    auth=HTTPBasicAuth(os.getenv("ES_USER"), os.getenv("ES_PASS")),
    json={
        "settings": {"number_of_shards": 1},
        "mappings": {"properties": {"test": {"type": "keyword"}}}
    }
)

print(resp.status_code, resp.text)
