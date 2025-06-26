from ppp_connectors.dbms import elasticsearch as es
from dotenv import load_dotenv, find_dotenv
import os
import json

load_dotenv(find_dotenv(filename=".env"))

client = es.get_elasticsearch_client([os.getenv("ES_HOST")])
query = {
    "query": {
        "match_all": {}
    }
}

print("Querying first 10 docs:")
for i, hit in enumerate(es.elasticsearch_query_scroll(client, index=os.getenv("ES_INDEX"), query=query)):
    print(json.dumps(hit, indent=2))
    if i >= 9:
        break

print("Inserting two test docs...")
es.elasticsearch_bulk_insert(client, os.getenv("ES_INDEX"), [{"test": 1}, {"test": 2}])