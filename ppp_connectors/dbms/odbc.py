import pyodbc
from typing import List, Dict, Any, Generator, Optional


def get_odbc_connection(conn_str: str) -> pyodbc.Connection:
    return pyodbc.connect(conn_str)

def odbc_query_paged(
    conn: pyodbc.Connection,
    base_query: str,
    page_size: int = 1000,
    offset: int = 0,
    max_results: Optional[int] = None,
    use_limit_offset: bool = True
) -> Generator[Dict[str, Any], None, None]:
    cursor = conn.cursor()
    fetched = 0

    while True:
        if use_limit_offset:
            paged_query = f"{base_query} LIMIT {page_size} OFFSET {offset}"
        else:
            paged_query = f"""
                SELECT * FROM (
                    SELECT ROW_NUMBER() OVER (ORDER BY 1) AS rownum, * FROM ({base_query}) as inner_query
                ) AS outer_query
                WHERE rownum > {offset} AND rownum <= {offset + page_size}
            """
        cursor.execute(paged_query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        if not rows:
            break
        for row in rows:
            yield dict(zip(columns, row))
            fetched += 1
            if max_results and fetched >= max_results:
                return
        offset += page_size

def odbc_bulk_insert(
    conn: pyodbc.Connection,
    table: str,
    data: List[Dict[str, Any]]
):
    if not data:
        return
    columns = list(data[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_str = ", ".join(columns)
    insert_query = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
    values = [tuple(row[col] for col in columns) for row in data]

    cursor = conn.cursor()
    cursor.fast_executemany = True
    cursor.executemany(insert_query, values)
    conn.commit()

# Thin wrapper API
def query(client, base_query, **kwargs):
    from ppp_connectors.dbms.broker import query as broker_query

    return broker_query(
        "odbc",
        client=client,
        query=None,
        base_query=base_query,
        **kwargs
    )

def bulk_insert(client, data, table, **kwargs):
    from ppp_connectors.dbms.broker import bulk_insert as broker_bulk_insert

    return broker_bulk_insert(
        "odbc",
        client=client,
        data=data,
        table=table,
        **kwargs
    )