from pymongo import MongoClient, UpdateOne
from typing import List, Dict, Any, Optional, Generator
from ppp_connectors.helpers import setup_logger


class MongoConnector:
    """
    A connector class for interacting with MongoDB.

    Provides methods for querying documents with paging and for performing bulk insert operations.
    Logs actions if a logger is provided.

    Args:
        uri (str): The MongoDB connection URI.
        username (Optional[str]): Username for authentication. Defaults to None.
        password (Optional[str]): Password for authentication. Defaults to None.
        auth_source (str): The authentication database. Defaults to "admin".
        timeout (int): Server selection timeout in seconds. Defaults to 10.
        auth_mechanism (Optional[str]): Authentication mechanism for MongoDB (e.g., "SCRAM-SHA-1").
        ssl (Optional[bool]): Whether to use SSL for the connection.
        logger (Optional[Any]): Logger instance for logging actions. Defaults to None.
    """
    def __init__(
        self,
        uri: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: str = "admin",
        timeout: int = 10,
        auth_mechanism: Optional[str] = "DEFAULT",
        ssl: Optional[bool] = True,
        logger: Optional[Any] = None
    ):
        """
        Initialize the MongoDB client.

        Args:
            uri (str): The MongoDB connection URI.
            username (Optional[str]): Username for authentication. Defaults to None.
            password (Optional[str]): Password for authentication. Defaults to None.
            auth_source (str): The authentication database. Defaults to "admin".
            timeout (int): Server selection timeout in seconds. Defaults to 10.
            auth_mechanism (Optional[str]): Authentication mechanism for MongoDB (e.g., "SCRAM-SHA-1").
            ssl (Optional[bool]): Whether to use SSL for the connection.
            logger (Optional[Any]): Logger instance for logging actions. Defaults to None.
        """
        # Initialize MongoClient with authSource, authMechanism, and ssl options
        self.client = MongoClient(
            uri,
            username=username,
            password=password,
            authSource=auth_source,
            authMechanism=auth_mechanism,
            ssl=ssl,
            serverSelectionTimeoutMS=timeout * 1000
        )
        self.logger = logger or setup_logger(__name__)
        self._log(
            f"Initialized MongoClient with authSource={auth_source}, "
            f"authMechanism={auth_mechanism}, ssl={ssl}"
        )

    def _log(self, msg: str, level: str = "info"):
        """
        Internal helper method for logging.

        Args:
            msg (str): The message to log.
            level (str): Logging level as string (e.g., "info", "debug"). Defaults to "info".
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

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

        Logs:
            Logs the query execution with filter details.
        """
        self._log(f"Executing Mongo query on {db_name}.{collection} with filter: {query}")
        col = self.client[db_name][collection]
        cursor = col.find(query, projection).batch_size(batch_size)
        for doc in cursor:
            yield doc

    def bulk_insert(
        self,
        db_name: str,
        collection: str,
        data: List[Dict],
        ordered: bool = False,
        batch_size: int = 1000,
        upsert: bool = False,
        unique_key: Optional[str] = None
    ):
        """
        Perform a bulk insert or upsert operation into a MongoDB collection.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            data (List[Dict]): List of documents to insert.
            ordered (bool): Whether the insert operations should be ordered. Defaults to False.
            batch_size (int): Number of documents per batch. Defaults to 1000.
            upsert (bool): If True, perform upserts instead of inserts. Requires unique_key.
            unique_key (Optional[str]): Field to use for upsert filtering. Required if upsert is True.

        Returns:
            List: List of InsertManyResult or BulkWriteResult objects for each batch.

        Logs:
            Logs the number of documents being inserted, the batch size, and the upsert flag.
        """
        if upsert and not unique_key:
            raise ValueError("unique_key must be provided when upsert is True")
        self._log(f"Inserting {len(data)} documents into {db_name}.{collection} with batch_size={batch_size}, upsert={upsert}")
        col = self.client[db_name][collection]
        results = []

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            if upsert and unique_key:
                operations = [
                    UpdateOne({unique_key: doc[unique_key]}, {"$set": doc}, upsert=True)
                    for doc in batch if unique_key in doc
                ]
                if operations:
                    result = col.bulk_write(operations, ordered=ordered)
                    results.append(result)
            else:
                result = col.insert_many(batch, ordered=ordered)
                results.append(result)

        return results
