from dotenv import load_dotenv, find_dotenv
from ppp_connectors.dbms import odbc
import os

load_dotenv(find_dotenv(filename=".env"))

conn = odbc.get_odbc_connection(os.getenv("ODBC_CONN_STR"))

base_query = "SELECT * FROM employees"  # adjust
print("Querying with pagination:")
for i, row in enumerate(odbc.odbc_query_paged(conn, base_query, page_size=10, use_limit_offset=True)):
    print(row)
    if i >= 9:
        break

# Optional insert test
# odbc.odbc_bulk_insert(conn, "your_table_here", [{"col1": "val1", "col2": "val2"}])