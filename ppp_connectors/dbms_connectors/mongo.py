from pymongo import MongoClient
from typing import List, Dict, Any, Optional, Generator


class MongoConnector:
    def __init__(
        self,
        uri: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: str = "admin"
    ):
        self.client = MongoClient(
            uri,
            username=username,
            password=password,
            authSource=auth_source
        )

    def query(
        self,
        db_name: str,
        collection: str,
        query: Dict,
        projection: Optional[Dict] = None,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        col = self.client[db_name][collection]
        cursor = col.find(query, projection).batch_size(batch_size)
        for doc in cursor:
            yield doc

    def bulk_insert(
        self,
        db_name: str,
        collection: str,
        data: List[Dict],
        ordered: bool = False
    ):
        col = self.client[db_name][collection]
        return col.insert_many(data, ordered=ordered)
