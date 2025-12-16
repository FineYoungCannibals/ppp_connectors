import asyncio
from typing import Any, Dict, List

from apiary.dbms_connectors.mongo_async import AsyncMongoConnector
from apiary.helpers import combine_env_configs, setup_logger


async def main() -> None:
    env: Dict[str, Any] = combine_env_configs()
    logger = setup_logger(name="mongo_dev_async", level="INFO")

    db = env["MONGO_DB"]
    col = env["MONGO_COLLECTION"]

    async with AsyncMongoConnector(
        uri=env["MONGO_URI"],
        username=env.get("MONGO_USER"),
        password=env.get("MONGO_PASS"),
        logger=logger,
        auth_source=env.get("MONGO_AUTH_SOURCE", "admin"),
        ssl=env.get("MONGO_SSL", False),
        auth_retry_attempts=int(env.get("MONGO_AUTH_RETRY_ATTEMPTS", 3)),
        auth_retry_wait=float(env.get("MONGO_AUTH_RETRY_WAIT", 1.0)),
    ) as client:
        # Clean up previous sample docs to avoid duplicate key issues on re-runs
        logger.info("[async] Wiping prior _sample documents with delete_many()...")
        await client.delete_many(db, col, {"_sample": True})

        # Prepare sample data
        docs: List[Dict[str, Any]] = [
            {"_id": 1, "name": "Alice", "role": "user", "tags": ["a", "b"], "_sample": True},
            {"_id": 2, "name": "Bob", "role": "admin", "tags": ["a"], "_sample": True},
            {"_id": 3, "name": "Carol", "role": "user", "tags": ["b"], "_sample": True},
        ]

        logger.info("[async] Inserting sample documents with insert_many()...")
        await client.insert_many(db, col, docs, ordered=False, batch_size=100)

        logger.info("[async] Upserting documents with upsert_many() using unique_key='_id'...")
        upserts: List[Dict[str, Any]] = [
            {"_id": 2, "name": "Bob", "role": "superadmin", "tags": ["a", "c"], "_sample": True},
            {"_id": 4, "name": "Dora", "role": "guest", "tags": ["c"], "_sample": True},
        ]
        await client.upsert_many(db, col, upserts, unique_key="_id", ordered=False, batch_size=100)

        # --- TEST CASE 1: upsert_many with single-field unique_key (string) ---
        logger.info("[async] Testing upsert_many with single-field unique_key (string)...")
        await client.delete_many(db, col, {"_sample_single": True})
        docs_single = [
            {"email": "alice@example.com", "score": 10, "_sample_single": True},
            {"email": "bob@example.com", "score": 20, "_sample_single": True},
        ]
        await client.insert_many(db, col, docs_single, ordered=False)
        upserts_single = [
            {"email": "bob@example.com", "score": 99, "_sample_single": True},  # Should update
            {"email": "carol@example.com", "score": 30, "_sample_single": True},  # Should insert
        ]
        await client.upsert_many(db, col, upserts_single, unique_key="email")
        logger.info("[async] Verifying single-field upsert results:")
        async for doc in client.find(
            db_name=db, collection=col, filter={"_sample_single": True}, projection={"_id": 0}
        ):
            print("[single-key upsert]", doc)

        # --- TEST CASE 2: upsert_many with compound unique_key (list of strings) ---
        logger.info("[async] Testing upsert_many with compound unique_key (list of strings)...")
        await client.delete_many(db, col, {"_sample_compound": True})
        docs_compound = [
            {"scan_uuid": "A1", "domain": "foo.com", "score": 5, "_sample_compound": True},
            {"scan_uuid": "A1", "domain": "bar.com", "score": 6, "_sample_compound": True},
            {"scan_uuid": "B2", "domain": "baz.com", "score": 7, "_sample_compound": True},
        ]
        await client.insert_many(db, col, docs_compound, ordered=False)
        upserts_compound = [
            # This should update an existing doc (A1, foo.com)
            {"scan_uuid": "A1", "domain": "foo.com", "score": 55, "_sample_compound": True},
            # This should insert a new doc (A1, qux.com)
            {"scan_uuid": "A1", "domain": "qux.com", "score": 66, "_sample_compound": True},
        ]
        await client.upsert_many(db, col, upserts_compound, unique_key=["scan_uuid", "domain"])
        logger.info("[async] Verifying compound-key upsert results:")
        async for doc in client.find(
            db_name=db, collection=col, filter={"_sample_compound": True}, projection={"_id": 0}
        ):
            print("[compound-key upsert]", doc)

        logger.info("[async] Finding _sample docs with projection and small batch size...")
        async for doc in client.find(
            db_name=db,
            collection=col,
            filter={"_sample": True},
            projection={"_id": 1, "name": 1, "role": 1},
            batch_size=2,
        ):
            print(doc)

        logger.info("[async] Getting distinct roles for _sample docs...")
        roles = await client.distinct(db, col, key="role", filter={"_sample": True})
        print("[async] Distinct roles:", roles)

        logger.info("[async] Running aggregate pipeline to count docs per role...")
        pipeline = [
            {"$match": {"_sample": True}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        async for doc in client.aggregate(db, col, pipeline, allowDiskUse=True):
            print("[async] Aggregated:", doc)


if __name__ == "__main__":
    asyncio.run(main())
