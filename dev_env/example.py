from ppp_connectors.dbms import mongo
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

client = mongo.get_mongo_client(f'mongodb://{env_config["MONGO_USER"]}:{env_config["MONGO_PASS"]}@{env_config["MONGO_URI"]}')

# Query
results = mongo.query(
    client=client,
    query={},
    db_name="test_db",
    collection="test_collection",
    page_size=100
)

for row in results:
    print(row)

# # Insert
# broker.bulk_insert(
#     backend=DBMSType.MONGO,
#     client=client,
#     data=[{"foo": "bar"}],
#     db_name="mydb",
#     collection="mycollection"
# )
