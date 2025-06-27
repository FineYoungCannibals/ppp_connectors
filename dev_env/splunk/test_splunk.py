from ppp_connectors.dbms import splunk
from ppp_connectors.helpers import combine_env_configs
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

service = splunk.get_splunk_service(
    host=env_config["SPLUNK_HOST"],
    port=int(env_config["SPLUNK_PORT"]),
    username=env_config["SPLUNK_USER"],
    password=env_config["SPLUNK_PASS"],
    scheme=env_config["SPLUNK_SCHEME"],
    verify=False
)


query = 'search index=_internal | head 20'

print("Streaming Splunk search results:")
for i, event in enumerate(splunk.splunk_query_paged(service, search=query)):
    print(event)
    if i >= 9:
        break