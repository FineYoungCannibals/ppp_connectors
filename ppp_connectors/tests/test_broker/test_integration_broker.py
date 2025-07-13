import httpx
from ppp_connectors.api_connectors.broker import Broker

def test_integration_get_with_mock_transport():
    def handler(request):
        assert request.url.path == "/hello"
        return httpx.Response(200, json={"msg": "ok"})

    transport = httpx.MockTransport(handler)
    broker = Broker(base_url="https://testserver", timeout=5)
    broker.session = httpx.Client(transport=transport)
    response = broker.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "ok"}
