from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Generator, Any


class ElasticsearchConnector:
    def __init__(
        self,
        hosts: List[str],
        username: str = "elastic",
        password: str = "changeme"
    ):
        self.client = Elasticsearch(hosts, basic_auth=(username, password))

    def query(
        self,
        index: str,
        query: Dict,
        size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        page = self.client.search(index=index, body=query, scroll="2m", size=size)
        sid = page["_scroll_id"]
        hits = page["hits"]["hits"]
        yield from hits

        while hits:
            page = self.client.scroll(scroll_id=sid, scroll="2m")
            sid = page["_scroll_id"]
            hits = page["hits"]["hits"]
            if not hits:
                break
            yield from hits
        self.client.clear_scroll(scroll_id=sid)

    def bulk_insert(
        self,
        index: str,
        data: List[Dict],
        id_key: str = "_id"
    ):
        actions = [
            {
                "_index": index,
                "_id": doc.get(id_key),
                "_source": doc
            } for doc in data
        ]
        return helpers.bulk(self.client, actions)