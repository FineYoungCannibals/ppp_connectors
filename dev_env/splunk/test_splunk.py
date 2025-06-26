from dotenv import load_dotenv, find_dotenv
from ppp_connectors.dbms import splunk
import os

load_dotenv(find_dotenv(filename=".env"))


service = splunk.get_splunk_service(
    host=os.getenv("SPLUNK_HOST"),
    port=int(os.getenv("SPLUNK_PORT")),
    username=os.getenv("SPLUNK_USER"),
    password=os.getenv("SPLUNK_PASS"),
    scheme=os.getenv("SPLUNK_SCHEME", "https"),
    verify=False
)


query = 'search index=_internal | head 20'

print("Streaming Splunk search results:")
for i, event in enumerate(splunk.splunk_query_paged(service, search=query)):
    print(event)
    if i >= 9:
        break