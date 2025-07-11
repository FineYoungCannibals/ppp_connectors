import unittest
from unittest.mock import patch, MagicMock
from ppp_connectors.dbms_connectors.elasticsearch import ElasticsearchConnector

class TestElasticsearchConnector(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )

    @patch("ppp_connectors.dbms_connectors.elasticsearch.Elasticsearch")
    def test_initialization(self, mock_es):
        ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )
        mock_es.assert_called_with(["http://localhost:9200"], basic_auth=("user", "pass"))

    @patch("ppp_connectors.dbms_connectors.elasticsearch.Elasticsearch")
    def test_query_scroll(self, mock_es):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "_scroll_id": "abc123",
            "hits": {"hits": [{"_id": 1}, {"_id": 2}]}
        }
        mock_client.scroll.side_effect = [
            {"_scroll_id": "abc123", "hits": {"hits": [{"_id": 3}]}},
            {"_scroll_id": "abc123", "hits": {"hits": []}},
        ]
        mock_es.return_value = mock_client
        connector = ElasticsearchConnector(
            hosts=["http://localhost:9200"],
            username="user",
            password="pass",
            logger=self.mock_logger
        )
        results = list(connector.query(index="test", query={"match_all": {}}))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["_id"], 1)

    @patch("ppp_connectors.dbms_connectors.elasticsearch.helpers.bulk")
    def test_bulk_insert(self, mock_bulk):
        mock_bulk.return_value = (3, [])
        data = [{"_id": "1", "name": "Alice"}, {"_id": "2", "name": "Bob"}, {"_id": "3", "name": "Charlie"}]
        success, errors = self.connector.bulk_insert(index="test-index", data=data)
        self.assertEqual(success, 3)
        self.assertEqual(errors, [])
        self.mock_logger.info.assert_called_with("Bulk insert completed successfully")

    @patch("ppp_connectors.dbms_connectors.elasticsearch.helpers.bulk")
    def test_bulk_insert_with_errors(self, mock_bulk):
        mock_bulk.return_value = (2, [{"error": "failed to insert"}])
        data = [{"_id": "1", "name": "Alice"}, {"_id": "2", "name": "Bob"}]
        success, errors = self.connector.bulk_insert(index="test-index", data=data)
        self.assertEqual(success, 2)
        self.assertTrue(errors)
        self.mock_logger.error.assert_called()

if __name__ == "__main__":
    unittest.main()