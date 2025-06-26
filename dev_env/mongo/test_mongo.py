from dotenv import load_dotenv, find_dotenv
from ppp_connectors.dbms import mongo
import os

load_dotenv(find_dotenv(filename=".env"))

client = mongo.get_mongo_client(os.getenv("MONGO_URI"))
col = mongo.get_collection(client, os.getenv("MONGO_DB"), os.getenv("MONGO_COLLECTION"))

print("Querying first 10 docs:")
for i, doc in enumerate(mongo.mongo_query_paged(col, {}, batch_size=5)):
    print(doc)
    if i >= 9:
        break

print("Inserting two test docs...")
mongo.mongo_bulk_insert(col, [{"test": 1}, {"test": 2}])