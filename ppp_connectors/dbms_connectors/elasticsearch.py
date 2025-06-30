from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Generator, Any


class ElasticsearchConnector:
    """
    A connector class for interacting with Elasticsearch.

    Provides methods for executing paginated queries using the scroll API
    and for performing bulk insert operations.
    """
    def __init__(
        self,
        hosts: List[str],
        username: str = "elastic",
        password: str = "changeme"
    ):
        """
        Initialize the Elasticsearch client.

        Args:
            hosts (List[str]): List of Elasticsearch host URLs.
            username (str): Username for basic authentication. Defaults to "elastic".
            password (str): Password for basic authentication. Defaults to "changeme".
        """
        self.client = Elasticsearch(hosts, basic_auth=(username, password))

    def query(
        self,
        index: str,
        query: Dict,
        size: int = 1000
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a paginated search query using the Elasticsearch scroll API.

        Args:
            index (str): The name of the index to search.
            query (Dict): The search query body.
            size (int): Number of results to retrieve per batch. Defaults to 1000.

        Yields:
            Dict[str, Any]: Each search hit as a dictionary.
        """
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
        """
        Perform a bulk insert operation into the specified index.

        Args:
            index (str): The name of the index to insert documents into.
            data (List[Dict]): A list of documents to insert.
            id_key (str): The key in each document to use as the document ID. Defaults to "_id".

        Returns:
            Tuple[int, List[Dict]]: A tuple containing the number of successfully processed actions
                                    and a list of any errors encountered.
        """
        actions = [
            {
                "_index": index,
                "_id": doc.get(id_key),
                "_source": doc
            } for doc in data
        ]
        return helpers.bulk(self.client, actions)