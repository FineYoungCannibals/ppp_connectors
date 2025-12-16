import asyncio
from typing import Any, Dict, Iterable, Tuple

from pyapiary.api_connectors.generic import AsyncGenericConnector

# Give AsyncGenericConnector lightweight context-manager support without
# modifying the library source.
if not hasattr(AsyncGenericConnector, "__aenter__"):
    async def _async_enter(self: AsyncGenericConnector) -> AsyncGenericConnector:
        return self

    async def _async_exit(
        self: AsyncGenericConnector,
        exc_type,
        exc,
        tb,
    ) -> None:
        await self.session.aclose()

    AsyncGenericConnector.__aenter__ = _async_enter        # type: ignore[attr-defined]
    AsyncGenericConnector.__aexit__ = _async_exit          # type: ignore[attr-defined]

RequestSpec = Tuple[str, str, Dict[str, Any]]

REQUESTS: Iterable[RequestSpec] = (
    ("GET", "/get", {"params": {"label": "alpha"}}),
    ("GET", "/delay/1", {"params": {"label": "beta"}}),
    ("GET", "/uuid", {"headers": {"X-Demo": "gamma"}}),
)


async def fetch(connector: AsyncGenericConnector, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    response = await connector.request(method, endpoint, **kwargs)
    return {
        "endpoint": endpoint,
        "status": response.status_code,
        "json": response.json(),
    }


async def main() -> None:
    async with AsyncGenericConnector(
        base_url="http://httpbin.org",
        enable_logging=False,
        timeout=15,
    ) as connector:
        tasks = [fetch(connector, method, endpoint, **req_kwargs) for method, endpoint, req_kwargs in REQUESTS]
        results = await asyncio.gather(*tasks)

    print("Completed concurrent requests:")
    for result in results:
        print(f"- {result['endpoint']} -> {result['status']}")
        print(f"  payload: {result['json']}")


if __name__ == "__main__":
    asyncio.run(main())
