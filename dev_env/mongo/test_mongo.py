from typing import Dict, Any, List
from apiary.dbms_connectors.mongo import MongoConnector
from apiary.helpers import combine_env_configs, setup_logger


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

        # --- Test upsert_many with single-field unique_key (string) ---
        print("\n--- upsert_many test: single-field unique_key ('email') ---")
        # Clean up any prior test docs
        client.delete_many(db, col, {"_test_email": True})
        email_docs = [
            {"email": "alice@example.com", "name": "Alice", "age": 30, "_test_email": True},
            {"email": "bob@example.com", "name": "Bob", "age": 25, "_test_email": True},
        ]
        client.insert_many(db, col, email_docs, ordered=False)
        # Upsert: update Bob, insert Carol
        email_upserts = [
            {"email": "bob@example.com", "name": "Bob", "age": 26, "_test_email": True},   # update
            {"email": "carol@example.com", "name": "Carol", "age": 22, "_test_email": True}, # insert
        ]
        client.upsert_many(db, col, email_upserts, unique_key="email", ordered=False)
        print("After upsert_many (email):")
        for doc in client.find(db, col, filter={"_test_email": True}, projection={"_id": 0, "email": 1, "name": 1, "age": 1}):
            print(doc)

        # --- Test upsert_many with compound unique_key (list of strings) ---
        print("\n--- upsert_many test: compound unique_key (['scan_uuid', 'domain']) ---")
        client.delete_many(db, col, {"_test_scan": True})
        scan_docs = [
            {"scan_uuid": "s1", "domain": "a.com", "result": "OK", "_test_scan": True},
            {"scan_uuid": "s2", "domain": "b.com", "result": "FAIL", "_test_scan": True},
        ]
        client.insert_many(db, col, scan_docs, ordered=False)
        # Upsert: update s2/b.com, insert s3/c.com
        scan_upserts = [
            {"scan_uuid": "s2", "domain": "b.com", "result": "PASS", "_test_scan": True},   # update
            {"scan_uuid": "s3", "domain": "c.com", "result": "OK", "_test_scan": True},     # insert
        ]
        client.upsert_many(db, col, scan_upserts, unique_key=["scan_uuid", "domain"], ordered=False)
        print("After upsert_many (compound):")
        for doc in client.find(
            db, col, filter={"_test_scan": True},
            projection={"_id": 0, "scan_uuid": 1, "domain": 1, "result": 1}
        ):
            print(doc)


if __name__ == "__main__":
    main()
