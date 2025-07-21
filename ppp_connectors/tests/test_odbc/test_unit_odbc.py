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
    """Test that query returns rows as dictionaries."""
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",), ("name",)]
    mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
    mock_connect.return_value.cursor.return_value = mock_cursor
    connector = ODBCConnector("DSN=testdb")

    results = list(connector.query("SELECT * FROM users"))

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


@patch("pyodbc.connect")
def test_odbcconnector_context_manager_closes_connection(mock_connect):
    """Test that the context manager closes the connection."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    with ODBCConnector("DSN=testdb") as connector:
        assert isinstance(connector, ODBCConnector)

    mock_conn.close.assert_called_once()