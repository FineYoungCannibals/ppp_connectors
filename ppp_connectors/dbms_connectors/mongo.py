from pymongo import MongoClient, UpdateOne
from pymongo.errors import (
    OperationFailure,
    ServerSelectionTimeoutError,
    AutoReconnect,
    ConnectionFailure,
)
from tenacity import Retrying, stop_after_attempt, wait_fixed, retry_if_exception_type
from typing import List, Dict, Any, Optional, Generator, Type, Union
from types import TracebackType
from ppp_connectors.helpers import setup_logger


_DEFAULT_LOGGER = object()


class MongoConnector:
    """
    A connector class for interacting with MongoDB.

    Provides methods for finding documents with paging and performing batched
    insert and upsert operations, as well as convenience helpers for
    `distinct`, `delete`, and `delete_many`.

    Supports explicit lifecycle management via `close()` and can be used as a
    context manager (`with MongoConnector(...) as conn:`). On initialization,
    the connector pings the server to validate connectivity/authentication with
    a simple retry policy.
    Logs actions if a logger is provided.
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
        logger: Optional[Any] = _DEFAULT_LOGGER,
        auth_retry_attempts: int = 3,
        auth_retry_wait: float = 1.0,
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
            logger (Optional[Any]): Logger instance for logging actions. Defaults to a module logger when omitted; pass None to disable logging.
            auth_retry_attempts (int): Number of attempts for initial auth ping. Defaults to 3.
            auth_retry_wait (float): Seconds to wait between auth attempts. Defaults to 1.0.
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
        self.logger = setup_logger(__name__) if logger is _DEFAULT_LOGGER else logger
        self.auth_retry_attempts = auth_retry_attempts
        self.auth_retry_wait = auth_retry_wait
        self._log(
            f"Initialized MongoClient with authSource={auth_source}, "
            f"authMechanism={auth_mechanism}, ssl={ssl}"
        )
        # Force an initial ping to trigger auth/handshake; retry to handle
        # clusters that intermittently fail the first attempt.
        self._ping_with_retry()

    def close(self) -> None:
        """Close the underlying MongoClient connection."""
        self._log("Closing MongoClient connection", level="debug")
        try:
            self.client.close()
        except Exception as exc:
            # Closing should be best-effort; log and continue
            self._log(f"Error during MongoClient.close(): {exc}", level="warning")

    # Context manager support
    def __enter__(self) -> "MongoConnector":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

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

    def _ping_with_retry(self) -> None:
        """Ping the server to validate connection/auth, with retry."""
        for attempt in Retrying(
            stop=stop_after_attempt(self.auth_retry_attempts),
            wait=wait_fixed(self.auth_retry_wait),
            reraise=True,
            retry=retry_if_exception_type(
                (OperationFailure, ServerSelectionTimeoutError, AutoReconnect, ConnectionFailure)
            ),
        ):
            with attempt:
                self._log("Pinging MongoDB to verify connection/auth...", level="debug")
                # 'ping' triggers handshake and, when needed, authentication
                self.client.admin.command("ping")

    def find(
        self,
        db_name: str,
        collection: str,
        filter: Dict,
        projection: Optional[Dict] = None,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Find documents in a MongoDB collection with optional projection and paging.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            filter (Dict): MongoDB filter document.
            projection (Optional[Dict]): Fields to include or exclude. Defaults to None.
            batch_size (int): Number of documents per batch. Defaults to 1000.

        Yields:
            Dict[str, Any]: Each document as a dictionary.

        Logs:
            Logs the find operation with filter details.
        """
        self._log(f"Executing Mongo find on {db_name}.{collection}")
        col = self.client[db_name][collection]
        cursor = col.find(filter, projection).batch_size(batch_size)
        for doc in cursor:
            yield doc

    def aggregate(
        self,
        db_name: str,
        collection: str,
        pipeline: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run an aggregation pipeline on a collection and stream results.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            pipeline (List[Dict[str, Any]]): Aggregation pipeline stages.
            batch_size (Optional[int]): If provided, set cursor batch size.
            **kwargs: Additional options forwarded to `Collection.aggregate` (e.g.,
                allowDiskUse, collation, maxTimeMS, comment).

        Yields:
            Dict[str, Any]: Each document from the aggregation result.
        """
        self._log(
            f"Executing Mongo aggregate on {db_name}.{collection}"
        )
        col = self.client[db_name][collection]
        cursor = col.aggregate(pipeline, **kwargs)
        if batch_size is not None:
            cursor = cursor.batch_size(batch_size)
        for doc in cursor:
            yield doc

    def query(
        self,
        db_name: str,
        collection: str,
        query: Dict,
        projection: Optional[Dict] = None,
        batch_size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Deprecated: use `find` instead.

        Backwards-compatible wrapper that forwards to `find`.
        """
        self._log(
            "MongoConnector.query is deprecated; use MongoConnector.find instead",
            level="warning",
        )
        return self.find(
            db_name=db_name,
            collection=collection,
            filter=query,
            projection=projection,
            batch_size=batch_size,
        )

    def insert_many(
        self,
        db_name: str,
        collection: str,
        data: List[Dict],
        ordered: bool = False,
        batch_size: int = 1000,
    ):
        """
        Insert multiple documents into a collection (batched).

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            data (List[Dict]): Documents to insert.
            ordered (bool): Whether operations should be ordered. Defaults to False.
            batch_size (int): Number of documents per batch. Defaults to 1000.

        Returns:
            List: List of InsertManyResult objects for each batch.

        Note:
            PyMongo batches writes internally; manual batching here is useful
            for memory control, error isolation, and progress logging.
        """
        self._log(
            f"insert_many: inserting {len(data)} docs into {db_name}.{collection} with batch_size={batch_size}"
        )
        col = self.client[db_name][collection]
        results = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            result = col.insert_many(batch, ordered=ordered)
            results.append(result)
        return results

    def upsert_many(
        self,
        db_name: str,
        collection: str,
        data: List[Dict],
        unique_key: Optional[Union[str, List[str]]],
        ordered: bool = False,
        batch_size: int = 1000,
    ):
        """
        Upsert multiple documents into a collection using a unique key or keys (batched).

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            data (List[Dict]): Documents to upsert.
            unique_key (Optional[Union[str, List[str]]]): Field name or list of field names to use for upsert filtering.
                If a list, the filter is built as a compound key using all specified fields.
            ordered (bool): Whether operations should be ordered. Defaults to False.
            batch_size (int): Number of documents per batch. Defaults to 1000.

        Returns:
            List: List of BulkWriteResult objects for each batch.

        Details:
            Uses `bulk_write` with `UpdateOne(filter, {"$set": doc}, upsert=True)`
            to merge fields from each document. The `unique_key` or all keys in the list
            must exist in each document.
        """
        if not unique_key:
            raise ValueError("unique_key must be provided for upsert_many")
        self._log(
            f"upsert_many: upserting {len(data)} docs into {db_name}.{collection} with batch_size={batch_size}, unique_key={unique_key}"
        )
        col = self.client[db_name][collection]
        results = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            operations = []
            for doc in batch:
                if isinstance(unique_key, str):
                    if unique_key in doc:
                        filter_doc = {unique_key: doc[unique_key]}
                    else:
                        continue
                elif isinstance(unique_key, list):
                    if all(k in doc for k in unique_key):
                        filter_doc = {k: doc[k] for k in unique_key}
                    else:
                        continue
                else:
                    raise ValueError("unique_key must be either a string or a list of strings")
                operations.append(UpdateOne(filter_doc, {"$set": doc}, upsert=True))
            if operations:
                result = col.bulk_write(operations, ordered=ordered)
                results.append(result)
        return results

    def distinct(
        self,
        db_name: str,
        collection: str,
        key: str,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Any]:
        """
        Return a list of distinct values for `key` across documents.

        This is a thin wrapper around PyMongo's `Collection.distinct` and accepts
        any additional keyword arguments supported by PyMongo (e.g., collation,
        maxTimeMS, comment).

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            key (str): Field name for which to return distinct values.
            filter (Optional[Dict[str, Any]]): Optional query filter to limit the scope.
            **kwargs: Additional options forwarded to `Collection.distinct`.

        Returns:
            List[Any]: Distinct values for the specified key.
        """
        self._log(
            f"Executing Mongo distinct on {db_name}.{collection} for key='{key}'"
        )
        col = self.client[db_name][collection]
        return col.distinct(key, filter, **kwargs)

    def delete(
        self,
        db_name: str,
        collection: str,
        filter: Dict[str, Any],
        **kwargs: Any,
    ):
        """
        Delete a single document matching the filter (wrapper over delete_one).

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Query filter selecting the document to delete.
            **kwargs: Additional options forwarded to `Collection.delete_one` (e.g., collation, comment).

        Returns:
            DeleteResult: The result of the delete operation.
        """
        self._log(
            f"Deleting one from {db_name}.{collection}",
            level="info",
        )
        col = self.client[db_name][collection]
        return col.delete_one(filter, **kwargs)

    def delete_many(
        self,
        db_name: str,
        collection: str,
        filter: Dict[str, Any],
        **kwargs: Any,
    ):
        """
        Delete all documents matching the filter (wrapper over delete_many).

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Query filter selecting documents to delete.
            **kwargs: Additional options forwarded to `Collection.delete_many` (e.g., collation, comment).

        Returns:
            DeleteResult: The result of the delete operation.
        """
        self._log(
            f"Deleting many from {db_name}.{collection}",
            level="info",
        )
        col = self.client[db_name][collection]
        return col.delete_many(filter, **kwargs)
