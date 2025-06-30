from ppp_connectors.dbms_connectors.odbc import ODBCConnector
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

conn = ODBCConnector(conn_str=env_config["PSQL_DSN"])

# Optional insert test
print("inserting one row")
conn.bulk_insert("employees", [{"name": "rob", "department": "hr"}])
base_query = "SELECT * FROM employees"

print("Querying with pagination:")
for i, row in enumerate(conn.query(base_query, page_size=10, use_limit_offset=True)):
    print(row)
    if i >= 9:
        break
