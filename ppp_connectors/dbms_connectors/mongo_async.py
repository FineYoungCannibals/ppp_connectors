from __future__ import annotations
from typing import Any, Dict, List, Optional, AsyncIterator, Type, Union
from types import TracebackType
import inspect
from pymongo import UpdateOne
from pymongo.errors import (
    OperationFailure,
    ServerSelectionTimeoutError,
    AutoReconnect,
    ConnectionFailure,
)
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed, retry_if_exception_type
from ppp_connectors.helpers import setup_logger


_DEFAULT_LOGGER = object()


class AsyncMongoConnector:
    """
    An asyncio connector for interacting with MongoDB using PyMongo's async client.

    Mirrors the synchronous MongoConnector API with async methods and context
    management (`async with AsyncMongoConnector(...) as conn:`). On entry, the
    connector pings the server with a simple retry policy to validate the
    connection and trigger authentication.

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
    ) -> None:
        # Import the asyncio client lazily to provide a clear error if unavailable
        AsyncMongoClient = None  # type: ignore
        import_error: Optional[Exception] = None
        try:
            from pymongo.asynchronous.mongo_client import AsyncMongoClient  # type: ignore
        except Exception as e1:  # pragma: no cover - fallback path
            import_error = e1
            try:
                # Some versions may expose it at package level
                from pymongo.asynchronous import AsyncMongoClient as _AltAsyncClient  # type: ignore
                AsyncMongoClient = _AltAsyncClient  # type: ignore
            except Exception as e2:  # pragma: no cover - fallback path
                import_error = e2
                try:
                    # Older preview namespace
                    from pymongo.asyncio import MongoClient as _AsyncioClient  # type: ignore
                    AsyncMongoClient = _AsyncioClient  # type: ignore
                except Exception as e3:  # pragma: no cover - final fallback
                    import_error = e3

        if AsyncMongoClient is None:  # type: ignore
            raise ImportError(
                "PyMongo async client is not available. Ensure a recent pymongo version is installed."
            ) from import_error

        self.client = AsyncMongoClient(  # type: ignore[misc]
            uri,
            username=username,
            password=password,
            authSource=auth_source,
            authMechanism=auth_mechanism,
            ssl=ssl,
            serverSelectionTimeoutMS=timeout * 1000,
        )
        self.logger = setup_logger(__name__) if logger is _DEFAULT_LOGGER else logger
        self._log(
            f"Initialized AsyncMongoClient with authSource={auth_source}, "
            f"authMechanism={auth_mechanism}, ssl={ssl}"
        )
        self.auth_retry_attempts = auth_retry_attempts
        self.auth_retry_wait = auth_retry_wait

    # Async context manager
    async def __aenter__(self) -> "AsyncMongoConnector":
        await self._ping_with_retry()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    def _log(self, msg: str, level: str = "info") -> None:
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

    async def _ping_with_retry(self) -> None:
        """Async ping to validate connection/auth, with retry."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.auth_retry_attempts),
            wait=wait_fixed(self.auth_retry_wait),
            reraise=True,
            retry=retry_if_exception_type(
                (OperationFailure, ServerSelectionTimeoutError, AutoReconnect, ConnectionFailure)
            ),
        ):
            with attempt:
                self._log("Pinging MongoDB (async) to verify connection/auth...", level="debug")
                await self.client.admin.command("ping")

    # Operations
    async def find(
        self,
        db_name: str,
        collection: str,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Async find documents with optional projection and paging.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            filter (Dict[str, Any]): MongoDB filter document.
            projection (Optional[Dict[str, Any]]): Fields to include/exclude.
            batch_size (int): Number of documents per batch.

        Yields:
            Each document as a dictionary.
        """
        self._log(
            f"Executing async Mongo find on {db_name}.{collection}"
        )
        col = self.client[db_name][collection]
        cursor = col.find(filter, projection).batch_size(batch_size)
        async for doc in cursor:
            yield doc

    async def aggregate(
        self,
        db_name: str,
        collection: str,
        pipeline: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Async aggregation pipeline execution yielding documents.

        Args:
            db_name (str): Name of the database.
            collection (str): Name of the collection.
            pipeline (List[Dict[str, Any]]): Aggregation pipeline stages.
            batch_size (Optional[int]): If provided, set cursor batch size.
            **kwargs: Additional options for `Collection.aggregate` (e.g., allowDiskUse).

        Yields:
            Each document from the aggregation result.

        Note:
            This returns an async iterator. Use `async for` to consume it.
            Do not `await` the return value directly.
        """
        self._log(
            f"Executing async Mongo aggregate on {db_name}.{collection}"
        )
        col = self.client[db_name][collection]
        # Some PyMongo async versions require awaiting aggregate() to get a cursor
        result = col.aggregate(pipeline, **kwargs)
        cursor = await result if inspect.isawaitable(result) else result
        if batch_size is not None:
            cursor = cursor.batch_size(batch_size)
        async for doc in cursor:
            yield doc

    async def insert_many(
        self,
        db_name: str,
        collection: str,
        data: List[Dict[str, Any]],
        ordered: bool = False,
        batch_size: int = 1000,
    ) -> List[Any]:
        """
        Async insert multiple documents into a collection (batched).

        Note:
            PyMongo batches writes internally as well; manual batching is
            primarily for progress logging, memory control, and error isolation.
        """
        self._log(
            f"async insert_many: inserting {len(data)} docs into {db_name}.{collection} with batch_size={batch_size}"
        )
        col = self.client[db_name][collection]
        results: List[Any] = []
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            result = await col.insert_many(batch, ordered=ordered)
            results.append(result)
        return results

    async def upsert_many(
        self,
        db_name: str,
        collection: str,
        data: List[Dict[str, Any]],
        unique_key: Optional[Union[str, List[str]]],
        ordered: bool = False,
        batch_size: int = 1000,
    ) -> List[Any]:
        """
        Async upsert multiple documents using a unique key (batched).

        Uses `bulk_write` with `UpdateOne(..., upsert=True)` and `$set` to
        merge fields from each document.

        Args:
            unique_key (Union[str, List[str]]): A string key or list of strings representing
                the unique key(s) used to build the filter for upsert operations.
                If a list is provided, it is treated as a compound unique key.
        """
        if not unique_key:
            raise ValueError("unique_key must be provided for upsert_many")
        if not (isinstance(unique_key, str) or (isinstance(unique_key, list) and all(isinstance(k, str) for k in unique_key))):
            raise ValueError("unique_key must be a string or a list of strings")
        self._log(
            f"async upsert_many: upserting {len(data)} docs into {db_name}.{collection} with batch_size={batch_size}, unique_key={unique_key}"
        )
        col = self.client[db_name][collection]
        results: List[Any] = []
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            operations = []
            for doc in batch:
                if isinstance(unique_key, str):
                    if unique_key in doc:
                        filter_doc = {unique_key: doc[unique_key]}
                    else:
                        continue
                else:
                    # unique_key is a list of strings
                    filter_doc = {k: doc[k] for k in unique_key if k in doc}
                    if len(filter_doc) != len(unique_key):
                        continue
                operations.append(UpdateOne(filter_doc, {"$set": doc}, upsert=True))
            if operations:
                result = await col.bulk_write(operations, ordered=ordered)
                results.append(result)
        return results

    async def distinct(
        self,
        db_name: str,
        collection: str,
        key: str,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Any]:
        """Async distinct values for a key, with optional filter."""
        self._log(
            f"Executing async Mongo distinct on {db_name}.{collection} for key='{key}'"
        )
        col = self.client[db_name][collection]
        return await col.distinct(key, filter, **kwargs)

    async def delete(
        self,
        db_name: str,
        collection: str,
        filter: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Async delete a single document matching the filter."""
        self._log(
            f"Async deleting one from {db_name}.{collection}",
            level="info",
        )
        col = self.client[db_name][collection]
        return await col.delete_one(filter, **kwargs)

    async def delete_many(
        self,
        db_name: str,
        collection: str,
        filter: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        """Async delete all documents matching the filter."""
        self._log(
            f"Async deleting many from {db_name}.{collection}",
            level="info",
        )
        col = self.client[db_name][collection]
        return await col.delete_many(filter, **kwargs)

    async def close(self) -> None:
        """Close the underlying async client."""
        self._log("Closing AsyncMongoClient connection", level="debug")
        try:
            result = self.client.close()
            if inspect.isawaitable(result):
                await result
        except Exception as exc:  # pragma: no cover - best-effort close
            self._log(f"Error during AsyncMongoClient.close(): {exc}", level="warning")
