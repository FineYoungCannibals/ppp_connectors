from ppp_connectors.dbms_connectors.mongo import MongoConnector
from ppp_connectors.helpers import combine_env_configs, setup_logger
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

# Initialize logger
logger = setup_logger(name="mongo_test", level="INFO")

print("Connecting to Mongo")
client = MongoConnector(
    uri=env_config["MONGO_URI"],
    username=env_config["MONGO_USER"],
    password=env_config["MONGO_PASS"],
    logger=logger,
    auth_source="admin",
    ssl=False
)


logger.info("Inserting two test docs...")
client.bulk_insert(
    env_config["MONGO_DB"],
    env_config["MONGO_COLLECTION"],
    [{"test": 1}, {"test": 2}]
)


logger.info("Performing a test query")
for i, doc in enumerate(client.query(
    db_name=env_config["MONGO_DB"],
    collection=env_config["MONGO_COLLECTION"],
    query={},
    projection=None,
    batch_size=100
)):
    print(doc)
