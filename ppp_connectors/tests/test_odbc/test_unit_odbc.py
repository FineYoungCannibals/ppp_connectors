

import pytest
from unittest.mock import MagicMock, patch
from ppp_connectors.dbms_connectors.odbc import ODBCConnector


@patch("pyodbc.connect")
def test_odbcconnector_init(mock_connect):
    mock_logger = MagicMock()
    connector = ODBCConnector("DSN=testdb", logger=mock_logger)
    mock_connect.assert_called_once_with("DSN=testdb")
    assert connector.logger == mock_logger


@patch("pyodbc.connect")
def test_odbcconnector_query_returns_rows(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",)]
    mock_cursor.fetchall.side_effect = [
        [(1, "Alice"), (2, "Bob")],
        []
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    results = list(connector.query("SELECT * FROM users", page_size=2))

    assert results == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


@patch("pyodbc.connect")
def test_odbcconnector_bulk_insert(mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    connector.bulk_insert("users", data)

    assert mock_cursor.executemany.called
    assert mock_connect.return_value.commit.called


@patch("pyodbc.connect")
def test_odbcconnector_bulk_insert_empty_data(mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    connector.bulk_insert("users", [])

    mock_cursor.executemany.assert_not_called()