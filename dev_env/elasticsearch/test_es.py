from apiary.dbms_connectors.elasticsearch import ElasticsearchConnector
from apiary.helpers import combine_env_configs, setup_logger
from typing import Dict, Any
import json


env_config: Dict[str, Any] = combine_env_configs()

# Initialize logger
logger = setup_logger(name="es_test", level="INFO")

# Pass logger into connector
client = ElasticsearchConnector(
    hosts=[env_config["ES_HOST"]],
    username=env_config["ES_USER"],
    password=env_config["ES_PASS"],
    logger=logger
)

logger.info("Inserting two test docs...")
client.bulk_insert(
    index=env_config["ES_INDEX"],
    data=[{"test": 1}, {"test": 2}]
)

query = {
    "query": {
        "match_all": {}
    }
}

logger.info("Querying first 10 docs:")
for i, hit in enumerate(client.query(index=env_config["ES_INDEX"], query=query)):
    print(json.dumps(hit, indent=2))
    if i >= 9:
        break
