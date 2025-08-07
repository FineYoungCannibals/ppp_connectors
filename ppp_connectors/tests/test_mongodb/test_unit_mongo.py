import pytest
from pymongo.errors import ServerSelectionTimeoutError
from ppp_connectors.dbms_connectors.mongo import MongoConnector
from unittest.mock import patch, MagicMock


def test_mongo_query(monkeypatch):
    mock_cursor = [
        {"_id": 1, "name": "Alice"},
        {"_id": 2, "name": "Bob"}
    ]
    mock_collection = MagicMock()
    mock_collection.find.return_value.batch_size.return_value = mock_cursor
    mock_db = {"test_collection": mock_collection}
    mock_client = {"test_db": mock_db}

    connector = MongoConnector(
        uri="mongodb://localhost:27017",
        username="fake",
        password="fake"
    )
    connector.client = mock_client

    results = list(connector.query("test_db", "test_collection", {}))
    assert results == mock_cursor


def test_bulk_insert(monkeypatch):
    mock_insert_many = MagicMock()
    mock_collection = {"insert_many": mock_insert_many}
    mock_db = {"test_collection": MagicMock(return_value=mock_insert_many)}
    mock_client = {"test_db": mock_db}

    connector = MongoConnector(
        uri="mongodb://localhost:27017",
        username="fake",
        password="fake"
    )
    connector.client = MagicMock()
    connector.client.__getitem__.return_value.__getitem__.return_value.insert_many = mock_insert_many

    test_data = [{"_id": 1}, {"_id": 2}]
    connector.bulk_insert("test_db", "test_collection", test_data)

    mock_insert_many.assert_called_once_with(test_data, ordered=False)


def test_mongo_connection_failure():
    connector = MongoConnector(
        uri="mongodb://localhost:27018", # invalid port
        username="fake",
        password="fake",
        timeout=1
    )
    with pytest.raises(ServerSelectionTimeoutError):
        list(connector.client.server_info())


# Additional tests for MongoConnector init with auth and ssl
from unittest.mock import patch

@patch("ppp_connectors.dbms_connectors.mongo.MongoClient")
def test_mongo_init_with_auth_and_ssl(mock_mongo_client):
    MongoConnector(
        uri="mongodb://example.com:27017",
        username="user",
        password="pass",
        auth_source="authdb",
        auth_mechanism="SCRAM-SHA-1",
        ssl=True
    )
    mock_mongo_client.assert_called_once_with(
        "mongodb://example.com:27017",
        username="user",
        password="pass",
        authSource="authdb",
        authMechanism="SCRAM-SHA-1",
        ssl=True,
        serverSelectionTimeoutMS=10000
    )


@patch("ppp_connectors.dbms_connectors.mongo.MongoClient")
def test_mongo_init_defaults(mock_mongo_client):
    MongoConnector(uri="mongodb://localhost:27017")
    mock_mongo_client.assert_called_once()
