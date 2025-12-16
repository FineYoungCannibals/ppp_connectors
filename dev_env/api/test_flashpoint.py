from pyapiary.api_connectors.flashpoint import FlashpointConnector
import httpx

fp = FlashpointConnector(
    load_env_vars=True,
    trust_env=True,
    verify=False,
    follow_redirects=True
)

# res = fp.search_communities('telegram')
# print(res)


try:
    resp = fp.get_media_image(
        "gs://kraken-datalake-media/artifacts/67/6739eed871575b5ad1864ea66d42ebf2430eda5f34d40715c9e40efe90232aa6",
        headers={},
        request_kwargs={"follow_redirects": True},
    )
    print("Final URL:", resp.url)
    print("Final status:", resp.status_code)
except httpx.HTTPStatusError as e:
    resp = e.response
    print("Final error:", resp.status_code, resp.url)

    # Show the chain of redirects
    for hop in resp.history:
        print("Redirect:", hop.status_code, hop.url, "->", hop.headers.get("location"))

    # Show body of final error if any
    print("Response body:", resp.text[:500])