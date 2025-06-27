from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Any, Generator


def get_elasticsearch_client(
    hosts: str,
    username: str,
    password: str
) -> Elasticsearch:
    return Elasticsearch([hosts], basic_auth=(username, password))


def elasticsearch_query_scroll(
    client: Elasticsearch,
    index: str,
    query: Dict,
    scroll: str = "2m",
    size: int = 1000
) -> Generator[Dict[str, Any], None, None]:
    page = client.search(index=index, body=query, scroll=scroll, size=size)
    sid = page['_scroll_id']
    hits = page['hits']['hits']
    yield from hits

    while hits:
        page = client.scroll(scroll_id=sid, scroll=scroll)
        sid = page['_scroll_id']
        hits = page['hits']['hits']
        if not hits:
            break
        yield from hits
    client.clear_scroll(scroll_id=sid)


def elasticsearch_bulk_insert(
    client: Elasticsearch,
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
    return helpers.bulk(client, actions)


# Thin wrapper API
def query(client, query, index, **kwargs):
    from ppp_connectors.dbms.broker import query as broker_query

    return broker_query(
        "elasticsearch",
        client=client,
        query=query,
        index=index,
        **kwargs
    )


def bulk_insert(client, data, index, **kwargs):
    from ppp_connectors.dbms.broker import bulk_insert as broker_bulk_insert

    return broker_bulk_insert(
        "elasticsearch",
        client=client,
        data=data,
        index=index,
        **kwargs
    )