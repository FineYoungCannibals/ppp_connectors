from typing import List, Dict, Any, Generator
import pyodbc


class ODBCConnector:
    """
    A connector class for interacting with ODBC-compatible databases.

    Provides methods for paginated queries and bulk inserts.
    """
    def __init__(self, conn_str: str):
        """
        Initialize the ODBC connection.

        Args:
            conn_str (str): The ODBC connection string.
        """
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

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
        """
        offset = 0
        while True:
            if use_limit_offset:
                paged_query = f"{base_query} LIMIT {page_size} OFFSET {offset}"
            else:
                paged_query = base_query
            self.cursor.execute(paged_query)
            columns = [column[0] for column in self.cursor.description]
            rows = self.cursor.fetchmany(page_size)
            if not rows:
                break
            for row in rows:
                yield dict(zip(columns, row))
            offset += page_size

    def bulk_insert(self, table: str, data: List[Dict]):
        """
        Perform a bulk insert into an ODBC database table.

        Args:
            table (str): Name of the table to insert into.
            data (List[Dict]): List of rows to insert.

        Returns:
            None
        """
        if not data:
            return
        columns = data[0].keys()
        placeholders = ", ".join(["?"] * len(columns))
        insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        values = [tuple(row[col] for col in columns) for row in data]
        self.cursor.executemany(insert_sql, values)
        self.conn.commit()