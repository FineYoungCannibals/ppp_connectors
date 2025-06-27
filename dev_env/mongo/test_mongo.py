from ppp_connectors.dbms import mongo
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

client = mongo.get_mongo_client(f'mongodb://{env_config["MONGO_USER"]}:{env_config["MONGO_PASS"]}@{env_config["MONGO_URI"]}')
col = mongo.get_collection(client, env_config["MONGO_DB"], env_config["MONGO_COLLECTION"])

print("Querying first 10 docs:")
for i, doc in enumerate(mongo.mongo_query_paged(col, {}, batch_size=5)):
    print(doc)
    if i >= 9:
        break

print("Inserting two test docs...")
mongo.mongo_bulk_insert(col, [{"test": 1}, {"test": 2}])