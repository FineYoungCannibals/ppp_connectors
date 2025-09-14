from ppp_connectors.dbms_connectors.mongo import MongoConnector
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()


client = MongoConnector(
    uri=env_config["MONGO_URI"],
    username=env_config["MONGO_USER"],
    password=env_config["MONGO_PASS"]
)

# Find
results = client.find(
    db_name=env_config["MONGO_DB"],
    collection=env_config["MONGO_COLLECTION"],
    filter={},
    projection=None,
    batch_size=100
)

for row in results:
    print(row)
