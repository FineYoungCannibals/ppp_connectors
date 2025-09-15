from typing import Dict, Any, List
from ppp_connectors.dbms_connectors.mongo import MongoConnector
from ppp_connectors.helpers import combine_env_configs, setup_logger


def main() -> None:
    env: Dict[str, Any] = combine_env_configs()
    logger = setup_logger(name="mongo_dev", level="INFO")

    db = env["MONGO_DB"]
    col = env["MONGO_COLLECTION"]

    logger.info("Connecting to Mongo with context manager...")
    with MongoConnector(
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
        logger.info("Wiping prior _sample documents with delete_many()...")
        client.delete_many(db, col, {"_sample": True})
        # Prepare sample data
        docs: List[Dict[str, Any]] = [
            {"_id": 1, "name": "Alice", "role": "user", "tags": ["a", "b"], "_sample": True},
            {"_id": 2, "name": "Bob", "role": "admin", "tags": ["a"], "_sample": True},
            {"_id": 3, "name": "Carol", "role": "user", "tags": ["b"], "_sample": True},
        ]

        logger.info("Inserting sample documents with insert_many()...")
        client.insert_many(db, col, docs, ordered=False, batch_size=100)

        logger.info("Upserting documents with upsert_many() using unique_key='_id'...")
        upserts: List[Dict[str, Any]] = [
            {"_id": 2, "name": "Bob", "role": "superadmin", "tags": ["a", "c"], "_sample": True},  # update existing
            {"_id": 4, "name": "Dora", "role": "guest", "tags": ["c"], "_sample": True},           # insert new
        ]
        client.upsert_many(db, col, upserts, unique_key="_id", ordered=False, batch_size=100)

        logger.info("Finding _sample docs with projection and small batch size...")
        for doc in client.find(
            db_name=db,
            collection=col,
            filter={"_sample": True},
            projection={"_id": 1, "name": 1, "role": 1},
            batch_size=2,
        ):
            print(doc)

        logger.info("Getting distinct roles for _sample docs...")
        roles = client.distinct(db, col, key="role", filter={"_sample": True})
        print("Distinct roles:", roles)

        logger.info("Running aggregate pipeline to count docs per role...")
        pipeline = [
            {"$match": {"_sample": True}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        for doc in client.aggregate(db, col, pipeline, allowDiskUse=True):
            print("Aggregated:", doc)


if __name__ == "__main__":
    main()
