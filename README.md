# ppp_connectors

A simple, lightweight set of connectors and functions to various APIs and DBMS backends, controlled by central broker modules. Includes support for API integrations (e.g., URLScan, Flashpoint) and DBMS systems (e.g., MongoDB, Elasticsearch, Splunk, ODBC).

## How to install

1. Install via pip to your environment:
   ```
   pip install ppp-connectors
   ```
2. Load the required environment variables. See `env.sample` or `.env` in `dev_env/`. This library automatically reads both `.env` files and system environment variables.

## How to use

### API connectors

Each API connector exposes functions that internally use the broker. Example:

```python
from ppp_connectors.urlscan import urlscan_search

r = urlscan_search('domain:google.com', size=200)
print(r.json())
```

### DBMS connectors

DBMS connectors expose `query` and `bulk_insert` functions that internally delegate to the DBMS broker. Example with MongoDB:

```python
from ppp_connectors.dbms.mongo import get_mongo_client, query, bulk_insert

client = get_mongo_client("mongodb://localhost:27017", username="root", password="example")
for doc in query(client, {"foo": "bar"}, db_name="testdb", collection="testcol"):
    print(doc)

bulk_insert(client, [{"foo": "bar"}], db_name="testdb", collection="testcol")
```

Example with Elasticsearch:

```python
from ppp_connectors.dbms.elasticsearch import get_elasticsearch_client, query

client = get_elasticsearch_client(["http://localhost:9200"], username="elastic", password="examplepassword")
for hit in query(client, {"query": {"match_all": {}}}, index="test-index"):
    print(hit)
```

## Passing additional parameters

All functions accept `**kwargs` for backend-specific options. Example:

```python
r = urlscan_search('domain:google.com', size=200)
```

or for ODBC:

```python
from ppp_connectors.dbms.odbc import get_odbc_connection, query

conn = get_odbc_connection("DSN=PostgresLocal;UID=postgres;PWD=postgres")
for row in query(conn, "SELECT * FROM my_table"):
    print(row)
```

## Notes

- The library supports MongoDB, Elasticsearch, Splunk, and ODBC DBMS backends.
- The DBMS connectors handle paging and bulk operations consistently.
- API connectors route through a central broker for consistency.


## Local development

To set up a local development environment:

1. Clone the repository:
   ```
   git clone https://github.com/your-org/ppp_connectors.git
   cd ppp_connectors
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Run tests:
   ```
   pytest
   ```

5. Lint and format:
   ```
   black .
   flake8 .
   ```

6. Spin up the dev environment (if using Docker):
   ```
   docker-compose up -d
   ```

Environment variables should be stored in `dev_env/.env` or loaded in your shell.
# ppp_connectors

A clean, lightweight set of connectors and utilities for interacting with APIs and DBMS backends. Designed for modular use with clear separation between API and DBMS connectors, supporting both functional and class-based patterns where appropriate.

## Installation

```
pip install ppp-connectors
```

Load environment variables from `dev_env/.env` or your shell environment as needed.

## API connectors

API connectors provide simple functional interfaces that use internal brokers to perform requests.

Example:

```python
from ppp_connectors.urlscan import urlscan_search

result = urlscan_search('domain:example.com', size=100)
print(result.json())
```

## DBMS connectors

DBMS connectors are now **class-based**, enabling connection reuse, transaction support, and advanced DBMS-specific features. Optional functional wrappers are provided for convenience.

### MongoDB

```python
from ppp_connectors.dbms_connectors.mongo import MongoConnector

conn = MongoConnector("mongodb://localhost:27017", username="root", password="example")
for doc in conn.query("testdb", "testcol", {"foo": "bar"}):
    print(doc)

conn.bulk_insert("testdb", "testcol", [{"foo": "bar"}])
```

### Elasticsearch

```python
from ppp_connectors.dbms_connectors.elasticsearch import ElasticsearchConnector

conn = ElasticsearchConnector(["http://localhost:9200"], username="elastic", password="examplepassword")
for hit in conn.query("test-index", {"query": {"match_all": {}}}):
    print(hit)

conn.bulk_insert("test-index", [{"_id": 1, "foo": "bar"}])
```

### ODBC

```python
from ppp_connectors.dbms_connectors.odbc import ODBCConnector

conn = ODBCConnector("DSN=PostgresLocal;UID=postgres;PWD=postgres")
for row in conn.query("SELECT * FROM my_table"):
    print(row)

conn.bulk_insert("my_table", [{"col1": "val1", "col2": "val2"}])
```

### Splunk

```python
from ppp_connectors.dbms_connectors.splunk import SplunkConnector

conn = SplunkConnector("localhost", 8089, "admin", "admin123", scheme="https", verify=False)
for result in conn.query("search index=_internal | head 10"):
    print(result)
```

## Local development

1. Clone the repo:
   ```
   git clone https://github.com/FineYoungCannibals/ppp_connectors.git
   cd ppp_connectors
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Run tests:
   ```
   pytest
   ```

5. Lint and format:
   ```
   black .
   flake8 .
   ```

6. Launch Docker dev environment:
   ```
   docker-compose up -d
   ```

## Notes

- API connectors still use a central broker pattern.
- DBMS connectors are class-based to support advanced DBMS features.
- Functional helpers are available for quick, stateless operations.