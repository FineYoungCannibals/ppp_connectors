from ppp_connectors.dbms_connectors.odbc import ODBCConnector
from ppp_connectors.helpers import combine_env_configs, setup_logger
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

# Initialize logger
logger = setup_logger(name="es_test", level="INFO")

conn = ODBCConnector(conn_str=env_config["PSQL_DSN"], logger=logger)

# Optional insert test
logger.info("inserting one row")
conn.bulk_insert("employees", [{"name": "rob", "department": "hr"}])
base_query = "SELECT * FROM employees"

logger.info("Querying with pagination:")
for i, row in enumerate(conn.query(base_query)):
    print(row)
    if i >= 9:
        break
