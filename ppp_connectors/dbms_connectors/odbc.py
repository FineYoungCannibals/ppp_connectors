import pyodbc
from typing import List, Dict, Generator, Any
from ppp_connectors.helpers import setup_logger


class ODBCConnector:
    """
    A connector class for interacting with ODBC-compatible databases.

    Provides methods for paginated queries and bulk inserts.
    Logs actions if a logger is provided.
    """

    def __init__(self, conn_str: str, logger: Any = None):
        """
        Initialize the ODBC connection.

        Args:
            conn_str (str): The ODBC connection string.
            logger (Any, optional): Logger instance for logging. Defaults to None.
        """
        self.conn = pyodbc.connect(conn_str)
        self.logger = logger or setup_logger(__name__)

    def _log(self, msg: str, level: str = "info"):
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

    def query(
        self,
        base_query: str,
        page_size: int = 1000,
        use_limit_offset: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a paginated query against an ODBC database.

        Args:
            base_query (str): The base SQL query.
            page_size (int): Number of rows per batch. Defaults to 1000.
            use_limit_offset (bool): Whether to use LIMIT/OFFSET for paging. Defaults to True.

        Yields:
            Dict[str, Any]: Each row as a dictionary.

        Logs:
            Execution details of the paginated query.
        """
        self._log(f"Executing paginated ODBC query with page size {page_size}")
        cursor = self.conn.cursor()
        offset = 0
        while True:
            if use_limit_offset:
                paged_query = f"{base_query} LIMIT {page_size} OFFSET {offset}"
            else:
                paged_query = base_query  # Enhance this for your use case
            cursor.execute(paged_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                break
            for row in rows:
                yield dict(zip(columns, row))
            offset += page_size

    def bulk_insert(self, table: str, data: List[Dict[str, Any]]):
        """
        Perform a bulk insert into an ODBC database table.

        Args:
            table (str): Name of the table to insert into.
            data (List[Dict[str, Any]]): List of rows to insert.

        Returns:
            None

        Logs:
            Number of rows inserted and target table.
        """
        if not data:
            return
        self._log(f"Inserting {len(data)} rows into table {table}")
        columns = list(data[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        values = [tuple(row[col] for col in columns) for row in data]
        cursor = self.conn.cursor()
        cursor.fast_executemany = True
        cursor.executemany(insert_query, values)
        self.conn.commit()
