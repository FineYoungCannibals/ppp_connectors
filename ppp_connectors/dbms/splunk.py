from splunklib.client import Service
from splunklib.results import JSONResultsReader
from typing import Dict, Generator, Any, Optional


def get_splunk_service(
    host: str,
    port: int,
    username: str,
    password: str,
    scheme: str = "https",
    verify: bool = True,
    autologin: bool = True
) -> Service:
    return Service(
        host=host,
        port=port,
        username=username,
        password=password,
        scheme=scheme,
        verify=verify,
        autologin=autologin
    )

def splunk_query_paged(
    service: Service,
    search: str,
    count: int = 1000,
    offset: int = 0,
    max_results: Optional[int] = None
) -> Generator[Dict[str, Any], None, None]:
    total_fetched = 0
    while True:
        job = service.jobs.create(search, count=count, offset=offset)
        while not job.is_ready():
            pass
        job.refresh()

        rr = JSONResultsReader(job.results(output_mode="json"))
        batch = [event for event in rr if isinstance(event, dict)]
        if not batch:
            break
        for event in batch:
            yield event
            total_fetched += 1
            if max_results and total_fetched >= max_results:
                return
        offset += count

# Thin wrapper API
def query(client, search, **kwargs):
    from ppp_connectors.dbms.broker import query as broker_query

    return broker_query(
        "splunk",
        client=client,
        query=search,
        **kwargs
    )