import requests
import time

def wait_for_es(url: str, timeout=60):
    for _ in range(timeout):
        try:
            if requests.get(url).status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    raise TimeoutError("Elasticsearch did not become available.")

wait_for_es("http://elasticsearch:9200")

# Example index creation
resp = requests.put("http://elasticsearch:9200/test-index", json={
    "settings": {"number_of_shards": 1},
    "mappings": {"properties": {"test": {"type": "keyword"}}}
})
print(resp.status_code, resp.text)