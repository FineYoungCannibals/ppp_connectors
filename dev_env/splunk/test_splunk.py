from pyapiary.dbms_connectors.splunk import SplunkConnector
from pyapiary.helpers import combine_env_configs, setup_logger
from typing import Dict, Any

env_config: Dict[str, Any] = combine_env_configs()

# Initialize logger
logger = setup_logger(name="es_test", level="INFO")

service = SplunkConnector(
    host=env_config["SPLUNK_HOST"],
    port=int(env_config["SPLUNK_PORT"]),
    username=env_config["SPLUNK_USER"],
    password=env_config["SPLUNK_PASS"],
    verify=False,
    logger=logger
)


query = 'search index=_internal | head 20'

logger.info("Streaming Splunk search results:")
for i, event in enumerate(service.query(search=query)):
    print(f'event sourcetype: {event["_sourcetype"]}')
    if i >= 9:
        break
