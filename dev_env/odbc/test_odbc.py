from ppp_connectors.dbms import odbc
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

conn = odbc.get_odbc_connection(env_config["ODBC_CONN_STR"])

base_query = "SELECT * FROM employees"  # adjust
print("Querying with pagination:")
for i, row in enumerate(odbc.odbc_query_paged(conn, base_query, page_size=10, use_limit_offset=True)):
    print(row)
    if i >= 9:
        break

# Optional insert test
# odbc.odbc_bulk_insert(conn, "your_table_here", [{"col1": "val1", "col2": "val2"}])