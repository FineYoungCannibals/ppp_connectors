import pytest
import requests
from unittest.mock import patch, MagicMock
from ppp_connectors.dbms_connectors.splunk import SplunkConnector


@pytest.fixture
def connector():
    return SplunkConnector(
        host="localhost",
        port=8089,
        username="admin",
        password="admin123",
        verify=False
    )


@patch("requests.post")
@patch("requests.get")
def test_query_success(mock_get, mock_post, connector):
    # Mock POST /services/search/jobs
    post_response = MagicMock()
    post_response.raise_for_status = MagicMock()
    post_response.json.return_value = {"sid": "abc123"}
    mock_post.return_value = post_response

    # Mock GET /services/search/jobs/{sid}
    get_status_response = MagicMock()
    get_status_response.raise_for_status = MagicMock()
    get_status_response.json.return_value = {
        "entry": [{"content": {"isDone": True}}]
    }

    # Mock GET /services/search/jobs/{sid}/results
    get_results_response = MagicMock()
    get_results_response.raise_for_status = MagicMock()
    get_results_response.json.side_effect = [
        {"results": [{"foo": "bar"}, {"baz": "qux"}]},
        {"results": []}
    ]
    mock_get.side_effect = [get_status_response, get_results_response, get_results_response]

    results = list(connector.query("search index=_internal | head 2"))
    assert len(results) == 2
    assert results[0]["foo"] == "bar"
    assert results[1]["baz"] == "qux"


@patch("requests.post")
def test_query_auth_error(mock_post, connector):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
    mock_post.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        list(connector.query("search index=_internal | head 1"))
