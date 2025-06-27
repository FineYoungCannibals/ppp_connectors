from ppp_connectors.dbms import elasticsearch as es
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any
import json

env_config: Dict[str, Any] = combine_env_configs()


client = es.get_elasticsearch_client(
    hosts=env_config["ES_HOST"],
    username=env_config["ES_USER"],
    password=env_config["ES_PASS"])
query = {
    "query": {
        "match_all": {}
    }
}

print("Querying first 10 docs:")
for i, hit in enumerate(es.elasticsearch_query_scroll(client, index=env_config["ES_INDEX"], query=query)):
    print(json.dumps(hit, indent=2))
    if i >= 9:
        break

print("Inserting two test docs...")
es.elasticsearch_bulk_insert(client, env_config["ES_INDEX"], [{"test": 1}, {"test": 2}])
