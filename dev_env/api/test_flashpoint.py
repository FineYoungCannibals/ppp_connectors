from ppp_connectors.api_connectors.flashpoint import FlashpointConnector

fp = FlashpointConnector(
    load_env_vars=True,
    trust_env=True,
    verify=False
)

res = fp.search_communities('telegram')
print(res)