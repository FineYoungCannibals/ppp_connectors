import pyodbc
from typing import List, Dict, Generator, Any


class ODBCConnector:
    def __init__(self, conn_str: str):
        self.conn = pyodbc.connect(conn_str)

    def query(
        self,
        base_query: str,
        page_size: int = 1000,
        use_limit_offset: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
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
        if not data:
            return
        columns = list(data[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        values = [tuple(row[col] for col in columns) for row in data]
        cursor = self.conn.cursor()
        cursor.fast_executemany = True
        cursor.executemany(insert_query, values)
        self.conn.commit()
