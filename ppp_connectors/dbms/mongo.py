from pymongo import MongoClient, InsertOne
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from typing import List, Dict, Optional, Generator, Any


def get_mongo_client(
    uri: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    auth_source: str = "admin"
) -> MongoClient:
    if username and password:
        return MongoClient(uri, username=username, password=password, authSource=auth_source)
    return MongoClient(uri)


def get_collection(client: MongoClient, db_name: str, collection_name: str) -> Collection:
    return client[db_name][collection_name]


def mongo_query_paged(
    col: Collection,
    query: Dict,
    projection: Optional[Dict] = None,
    batch_size: int = 1000
) -> Generator[Dict[str, Any], None, None]:
    cursor: Cursor = col.find(query, projection).batch_size(batch_size)
    for doc in cursor:
        yield doc


def mongo_bulk_insert(
    col: Collection,
    data: List[Dict],
    ordered: bool = False
):
    ops = [InsertOne(doc) for doc in data]
    result = col.bulk_write(ops, ordered=ordered)
    return result


# Thin wrapper API
def query(client, query, db_name, collection, **kwargs):
    from ppp_connectors.dbms.broker import query as broker_query

    return broker_query(
        "mongo",
        client=client,
        query=query,
        db_name=db_name,
        collection=collection,
        **kwargs
    )


def bulk_insert(client, data, db_name, collection, **kwargs):
    from ppp_connectors.dbms.broker import bulk_insert as broker_bulk_insert

    return broker_bulk_insert(
        "mongo",
        client=client,
        data=data,
        db_name=db_name,
        collection=collection,
        **kwargs
    )