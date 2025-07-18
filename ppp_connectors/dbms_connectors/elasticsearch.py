from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Generator, Any, Optional, Union


try:
    from ppp_connectors.helpers import setup_logger
    _default_logger = setup_logger(name="elasticsearch")
except ImportError:
    import logging
    _default_logger = logging.getLogger("elasticsearch")
    if not _default_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        _default_logger.addHandler(handler)
    _default_logger.setLevel(logging.INFO)


class ElasticsearchConnector:
    """
    A connector class for interacting with Elasticsearch.

    This class provides methods to perform paginated search queries using the scroll API
    and to execute bulk insert operations. It includes integrated logging support for observability.
    """
    def __init__(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize the Elasticsearch client.

        Args:
            hosts (List[str]): List of Elasticsearch host URLs.
            username (Optional[str]): Username for basic authentication. Defaults to None.
            password (Optional[str]): Password for basic authentication. Defaults to None.
            logger (Optional[Any]): Optional logger instance. If not provided, a default logger is used.
        """
        self.client = Elasticsearch(hosts, basic_auth=(username, password))
        self.logger = logger if logger is not None else _default_logger

    def _log(self, msg: str, level: str = "info"):
        """
        Internal helper to log messages using the provided or default logger.

        Args:
            msg (str): The message to log.
            level (str): The logging level as a string (e.g., 'info', 'error'). Defaults to 'info'.
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

    def query(
        self,
        index: str,
        query: Union[str, Dict],
        size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a paginated search query using the Elasticsearch scroll API.

        This method handles retrieval of large result sets by paging through results
        using a scroll context.

        Args:
            index (str): The name of the index to search.
            query (Union[str, Dict]): A Lucene query string or Elasticsearch DSL query body.
            size (int): Number of results to retrieve per batch. Defaults to 1000.

        Yields:
            Generator[Dict[str, Any], None, None]: A generator that yields each search hit as a dictionary.

        Note:
            This method returns a generator. If you want to collect all results,
            you can wrap the result in `list()`, but beware of memory usage if the
            result set is large. Prefer streaming and processing results incrementally.
        """

        self._log(f"Executing query on index '{index}' with batch size {size}", "info")

        if isinstance(query, str):
            query = {
                "query": {
                    "query_string": {
                        "query": query
                    }
                }
            }

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
        self._log(f"Completed scrolling query on index '{index}'", "info")

    def bulk_insert(
        self,
        index: str,
        data: List[Dict],
        id_key: str = "_id"
    ):
        """
        Perform a bulk insert operation into the specified Elasticsearch index.

        This method sends batches of documents for indexing in a single API call.
        Each document can optionally specify an ID via the `id_key`.

        Args:
            index (str): The name of the index to insert documents into.
            data (List[Dict]): A list of documents to insert.
            id_key (str): The key in each document to use as the document ID. Defaults to "_id".

        Returns:
            Tuple[int, List[Dict]]: A tuple containing the number of successfully processed actions
                                    and a list of any errors encountered during insertion.
        """
        self._log(f"Inserting {len(data)} documents into index '{index}'", "info")
        actions = [
            {
                "_index": index,
                "_id": doc.get(id_key),
                "_source": doc
            } for doc in data
        ]
        success, errors = helpers.bulk(self.client, actions)
        if errors:
            self._log(f"Bulk insert encountered errors: {errors}", "error")
        else:
            self._log("Bulk insert completed successfully", "info")
        return success, errors
