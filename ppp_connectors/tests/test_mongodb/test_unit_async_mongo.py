import sys
import types
import pytest
from unittest.mock import AsyncMock

from ppp_connectors.dbms_connectors.mongo_async import AsyncMongoConnector


@pytest.mark.asyncio
async def test_async_init_and_ping(monkeypatch):
    fake_client = types.SimpleNamespace()
    fake_client.admin = types.SimpleNamespace()
    fake_client.admin.command = AsyncMock(return_value={"ok": 1})

    # Provide pymongo.asyncio.MongoClient for import inside the connector
    ns = types.SimpleNamespace(AsyncMongoClient=lambda *a, **k: fake_client)
    monkeypatch.setitem(sys.modules, "pymongo.asynchronous.mongo_client", ns)

    async with AsyncMongoConnector(uri="mongodb://localhost:27017") as conn:
        assert isinstance(conn, AsyncMongoConnector)

    fake_client.admin.command.assert_awaited_once_with("ping")


class _AsyncCursor:
    def __init__(self, items):
        self._items = items
        self._idx = 0

    def batch_size(self, n):
        return self

    def __aiter__(self):
        self._idx = 0
        return self

    async def __anext__(self):
        if self._idx >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._idx]
        self._idx += 1
        return item


@pytest.mark.asyncio
async def test_async_find(monkeypatch):
    docs = [{"_id": 1}, {"_id": 2}]

    class _FakeCollection:
        def find(self, f, p):
            return _AsyncCursor(docs)

    class _FakeDB(dict):
        def __getitem__(self, k):
            return _FakeCollection()

    class _FakeClient:
        def __init__(self):
            self.admin = types.SimpleNamespace()
            self.admin.command = AsyncMock(return_value={"ok": 1})

        def __getitem__(self, k):
            return _FakeDB()

        def close(self):
            pass

    fake_client = _FakeClient()
    ns = types.SimpleNamespace(AsyncMongoClient=lambda *a, **k: fake_client)
    monkeypatch.setitem(sys.modules, "pymongo.asynchronous.mongo_client", ns)

    async with AsyncMongoConnector(uri="mongodb://localhost:27017") as conn:
        out = [doc async for doc in conn.find("db", "col", filter={})]

    assert out == docs
