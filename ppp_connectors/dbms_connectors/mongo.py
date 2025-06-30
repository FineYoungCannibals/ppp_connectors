from pymongo import MongoClient
from typing import List, Dict, Any, Optional, Generator


class MongoConnector:
    """
    A connector class for interacting with MongoDB.

    Provides methods for querying documents with paging and for performing bulk insert operations.
    """
    def __init__(
        self,
        uri: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: str = "admin"
    ):
        """
        Initialize the MongoDB client.

        Args:
            uri (str): The MongoDB connection URI.
            username (Optional[str]): Username for authentication. Defaults to None.
            password (Optional[str]): Password for authentication. Defaults to None.
            auth_source (str): The authentication database. Defaults to "admin".
        """
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
        """
        Execute a paginated query against a MongoDB collection.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            query (Dict): MongoDB query filter.
            projection (Optional[Dict]): Fields to include or exclude. Defaults to None.
            batch_size (int): Number of documents per batch. Defaults to 1000.

        Yields:
            Dict[str, Any]: Each document as a dictionary.
        """
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
        """
        Perform a bulk insert operation into a MongoDB collection.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            data (List[Dict]): List of documents to insert.
            ordered (bool): Whether the insert operations should be ordered. Defaults to False.

        Returns:
            InsertManyResult: The result of the bulk insert operation.
        """
        col = self.client[db_name][collection]
        return col.insert_many(data, ordered=ordered)
