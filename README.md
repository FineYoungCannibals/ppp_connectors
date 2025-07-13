# ppp_connectors


A clean, modular set of Python connectors and utilities for working with both **APIs** and **DBMS backends**, unified by a centralized `Broker` abstraction and a consistent interface. Designed for easy testing, code reuse, and plug-and-play extensibility.


## 📚 Table of Contents

- [Installation](#installation)
- [API Connectors](#api-connectors)
  - [Example (URLScan)](#example-urlscan)
  - [Customizing API Requests with **kwargs](#customizing-api-requests-with-kwargs)
- [DBMS Connectors](#dbms-connectors)
  - [MongoDB](#mongodb)
  - [Elasticsearch](#elasticsearch)
  - [ODBC](#odbc-eg-postgres-teradata)
  - [Splunk](#splunk)
- [Testing](#testing)
  - [Unit tests](#unit-tests)
  - [Integration tests](#integration-tests)
  - [Suppress warnings](#suppress-warnings)
- [Contributing / Adding a Connector](#contributing--adding-a-connector)
- [Dev Environment](#dev-environment)
- [Secrets and Redaction](#secrets-and-redaction)
- [Summary](#summary)



---

## 📦 Installation

```bash
pip install ppp-connectors
```

Copy the `.env.example` to `.env` for local development:

```bash
cp dev_env/.env.example dev_env/.env
```

Environment variables are loaded automatically via the `combine_env_configs()` helper.

---

## 🔌 API Connectors

All API connectors inherit from the shared `Broker` base class and:
- Accept API credentials via env vars or constructor args
- Send requests via `get`, `post`, etc.
- Include support for logging, retry/backoff, and VCR integration
- Support

### Example (URLScan)

```python
from ppp_connectors.api_connectors.urlscan import URLScanConnector

scanner = URLScanConnector(load_env_vars=True)
result = scanner.scan(
    url="https://example.com",
    visibility="public",
    tags=["example", "demo"],
    custom={"foo": "bar"},  # Arbitrary API field passed via **kwargs
    headers={"X-Custom-Header": "my-value"}  # httpx headers
)
print(result.json())
```

### Customizing API Requests with **kwargs

All connector methods accept arbitrary keyword arguments using `**kwargs`. These arguments are passed directly to the underlying `httpx` request methods, enabling support for any feature available in [`httpx`](https://www.python-httpx.org/api/#request) — including custom headers, query parameters, timeouts, authentication, and more. Additionally, for APIs that accept arbitrary fields in their request body (like `URLScan`), these can also be passed as part of `**kwargs` and will be merged into the outgoing request. This enables full control over how API requests are constructed without needing to modify connector internals.

#### Example (URLScan with custom headers and params)

```python
result = scanner.scan(
    url="https://example.com",
    visibility="unlisted",
    headers={"X-Custom-Header": "my-value"},
    params={"pretty": "true"}
)
```

This pattern allows flexibility without needing to subclass or modify the connector.

---

## 🗃️ DBMS Connectors

Each database connector follows a class-based pattern and supports reusable sessions, query helpers, and in some cases `bulk_insert`.

### MongoDB

```python
from ppp_connectors.dbms_connectors.mongo import MongoConnector

conn = MongoConnector("mongodb://localhost:27017", username="root", password="example")
conn.bulk_insert("mydb", "mycol", [{"foo": "bar"}])
```

### Elasticsearch

```python
from ppp_connectors.dbms_connectors.elasticsearch import ElasticsearchConnector

conn = ElasticsearchConnector(["http://localhost:9200"])
conn.query("my-index", {"query": {"match_all": {}}})
```

### ODBC (e.g., Postgres, Teradata)

```python
from ppp_connectors.dbms_connectors.odbc import ODBCConnector

conn = ODBCConnector("DSN=PostgresLocal;UID=postgres;PWD=postgres")
rows = conn.query("SELECT * FROM my_table")
```

### Splunk

```python
from ppp_connectors.dbms_connectors.splunk import SplunkConnector

conn = SplunkConnector("localhost", 8089, "admin", "admin123", scheme="https", verify=False)
results = conn.query("search index=_internal | head 5")
```

---

## 🧪 Testing

### ✅ Unit tests

- Located in `tests/<connector_name>/test_unit_<connector>.py`
- Use mocking (`MagicMock`, `patch`) to avoid hitting external APIs

### 🔁 Integration tests

- Use [VCR.py](https://github.com/kevin1024/vcrpy) to record HTTP interactions
- Cassettes stored in: `tests/<connector_name>/cassettes/`
- Automatically redact secrets (API keys, tokens, etc.)
- Marked with `@pytest.mark.integration`

```bash
pytest -m integration
```

### 🧼 Suppress warnings

Add this to `pytest.ini`:

```ini
[pytest]
markers =
    integration: marks integration tests
```

---

## 🧑‍💻 Contributing / Adding a Connector

To add a new connector:

1. **Module**: Place your module in:
   - `ppp_connectors/api_connectors/` for API-based integrations
   - `ppp_connectors/dbms_connectors/` for database-style connectors

2. **Base class**:
   - Use the `Broker` class for APIs
   - Use the appropriate DBMS connector template for DBMSs

3. **Auth**: Pull secrets using `combine_env_configs()` to support `.env`, environment variables, and CI/CD injection.

4. **Testing**:
   - Add unit tests in: `tests/<name>/test_unit_<connector>.py`
   - Add integration tests in: `tests/<name>/test_integration_<connector>.py`
   - Save cassettes in: `tests/<name>/cassettes/`

5. **Docs**:
   - Add an example usage to this `README.md`
   - Document all methods with docstrings
   - Ensure your connector supports logging if `enable_logging=True` is passed

6. **Export**:
   - Optionally expose your connector via `__init__.py` for easier importing

---

## 🛠️ Dev Environment

```bash
git clone https://github.com/FineYoungCannibals/ppp_connectors.git
cd ppp_connectors

cp .env.example .env

python -m venv .venv
source .venv/bin/activate

poetry install  # if using poetry, or `pip install -e .[dev]`

pytest           # run all tests
black .          # format code
flake8 .         # linting
```

---

## 🔐 Secrets and Redaction

Sensitive values like API keys are redacted using the `AUTH_PARAM_REDACT` list in `conftest.py`. This ensures `.yaml` cassettes don’t leak credentials.

Redacted fields include:
- Query/body fields like `api_key`, `key`, `token`
- Header fields like `Authorization`, `X-API-Key`
- URI query parameters

---

## ✅ Summary

- Centralized request broker for all APIs
- Robust DBMS connectors
- Easy-to-write unit and integration tests with automatic redaction
- Environment-agnostic configuration system
- VCR-powered CI-friendly test suite
