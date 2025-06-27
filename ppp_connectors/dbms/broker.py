from typing import Any, List, Dict, Generator, Optional, Union

from ppp_connectors.dbms import (
    mongo,
    elasticsearch,
    splunk,
    odbc
)

VALID_DBMS = {"mongo", "elasticsearch", "splunk", "odbc"}

QueryResult = Generator[Dict[str, Any], None, None]
BulkData = List[Dict[str, Any]]

def query(
    backend: str,
    client: Any,
    query: Union[str, Dict],
    *,
    db_name: Optional[str] = None,
    collection: Optional[str] = None,
    index: Optional[str] = None,
    table: Optional[str] = None,
    base_query: Optional[str] = None,
    use_limit_offset: Optional[bool] = True,
    page_size: int = 1000,
    **kwargs
) -> QueryResult:
    """
    Dispatch a query to the specified backend DBMS and return results as a generator of dictionaries.

    Args:
        backend (str): The name of the DBMS backend ("mongo", "elasticsearch", "splunk", "odbc").
        client (Any): The DBMS client or connection object.
        query (Union[str, Dict]): The query to execute. For Mongo and Elasticsearch, this is a dict; for Splunk and ODBC, a string.
        db_name (Optional[str]): The database name (Mongo only).
        collection (Optional[str]): The collection name (Mongo only).
        index (Optional[str]): The index name (Elasticsearch only).
        table (Optional[str]): The table name (ODBC only).
        base_query (Optional[str]): The base SQL query (ODBC only).
        use_limit_offset (Optional[bool]): Whether to use LIMIT/OFFSET paging (ODBC only).
        page_size (int): The page size for paged queries.
        **kwargs: Additional backend-specific parameters.

    Returns:
        Generator[Dict[str, Any], None, None]: A generator of result rows as dictionaries.

    Raises:
        ValueError: If required parameters are missing for the specified backend.
        NotImplementedError: If the backend is unsupported or not handled.
    """

    if backend not in VALID_DBMS:
        raise ValueError(f"Unsupported backend: {backend}")

    if backend == "mongo":
        if not db_name or not collection:
            raise ValueError("Mongo requires db_name and collection")
        col = mongo.get_collection(client, db_name, collection)
        return mongo.mongo_query_paged(col, query, batch_size=page_size, **kwargs)

    if backend == "elasticsearch":
        if not index:
            raise ValueError("Elasticsearch requires index")
        return elasticsearch.elasticsearch_query_scroll(
            client, index=index, query=query, size=page_size, **kwargs
        )

    if backend == "splunk":
        return splunk.splunk_query_paged(
            client, search=query, count=page_size, **kwargs
        )

    if backend == "odbc":
        if not base_query:
            raise ValueError("ODBC requires base_query")
        return odbc.odbc_query_paged(
            conn=client,
            base_query=base_query,
            page_size=page_size,
            use_limit_offset=use_limit_offset,
            **kwargs
        )

    raise NotImplementedError(f"Unhandled backend: {backend}")

def bulk_insert(
    backend: str,
    client: Any,
    data: BulkData,
    *,
    db_name: Optional[str] = None,
    collection: Optional[str] = None,
    index: Optional[str] = None,
    table: Optional[str] = None,
    **kwargs
):
    """
    Dispatch a bulk insert operation to the specified backend DBMS.

    Args:
        backend (str): The name of the DBMS backend ("mongo", "elasticsearch", "odbc").
        client (Any): The DBMS client or connection object.
        data (List[Dict]): The data to insert.
        db_name (Optional[str]): The database name (Mongo only).
        collection (Optional[str]): The collection name (Mongo only).
        index (Optional[str]): The index name (Elasticsearch only).
        table (Optional[str]): The table name (ODBC only).
        **kwargs: Additional backend-specific parameters.

    Returns:
        Any: The result of the bulk insert operation.

    Raises:
        ValueError: If required parameters are missing for the specified backend.
        NotImplementedError: If the backend does not support bulk insert or is not handled.
    """
    if backend not in VALID_DBMS:
        raise ValueError(f"Unsupported backend: {backend}")

    if backend == "mongo":
        if not db_name or not collection:
            raise ValueError("Mongo requires db_name and collection")
        col = mongo.get_collection(client, db_name, collection)
        return mongo.mongo_bulk_insert(col, data, **kwargs)

    if backend == "elasticsearch":
        if not index:
            raise ValueError("Elasticsearch requires index")
        return elasticsearch.elasticsearch_bulk_insert(client, index=index, data=data, **kwargs)

    if backend == "odbc":
        if not table:
            raise ValueError("ODBC requires table")
        return odbc.odbc_bulk_insert(client, table=table, data=data, **kwargs)

    if backend == "splunk":
        raise NotImplementedError("Splunk does not support bulk_insert in this broker")

    raise NotImplementedError(f"Unhandled backend: {backend}")