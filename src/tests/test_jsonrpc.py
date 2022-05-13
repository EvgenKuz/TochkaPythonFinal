import json

import pytest

from .. import App
from aiohttp.pytest_plugin import TestClient
from aiohttp.client import ClientResponse


@pytest.fixture
async def client(aiohttp_client) -> TestClient:
    return await aiohttp_client(App.init())


async def test_jsonrpc_method_test(client: TestClient) -> None:
    jsonrpc_body = {"jsonrpc": "2.0", "method": "test", "params": {"a": 2}, "id": 1}
    resp: ClientResponse = await client.post("/api/v1/jsonrpc",
                                             data=json.dumps(jsonrpc_body))
    assert resp.status == 200

    response = await resp.json()
    assert response["result"] == "ok"


async def test_jsonrpc_parse_error(client: TestClient) -> None:
    resp: ClientResponse = await client.post("/api/v1/jsonrpc", data='ff')
    ans = await resp.json()

    assert ans["error"]["code"] == -32700
    assert ans["error"]["message"] == "Parse error"


async def test_jsonrpc_invalid_request(client: TestClient) -> None:
    req = {"jsonrpc": "2.0", "method": 2}
    resp: ClientResponse = await client.post("/api/v1/jsonrpc", data=json.dumps(req))
    ans = await resp.json()

    assert ans["error"]["code"] == -32600
    assert ans["error"]["message"] == "Invalid request"


async def test_jsonrpc_method_not_found_error(client: TestClient) -> None:
    req = {"jsonrpc": "2.0", "method": "no", "id": 1}
    resp = await client.post("/api/v1/jsonrpc", data=json.dumps(req))
    ans = await resp.json()

    assert ans["error"]["code"] == -32601
    assert ans["error"]["message"] == "Method not found"


async def test_jsonrpc_invalid_params_error(client: TestClient) -> None:
    req = {"jsonrpc": "2.0", "method": "test", "params": {"b": 2}, "id": 1}
    resp = await client.post("/api/v1/jsonrpc", data=json.dumps(req))
    ans = await resp.json()

    assert ans["error"]["code"] == -32602
    assert ans["error"]["message"] == "Invalid params"


async def test_jsonrpc_internal_error(client: TestClient) -> None:
    req = {"jsonrpc": "2.0", "method": "internal_error", "id": 1}
    resp = await client.post("/api/v1/jsonrpc", data=json.dumps(req))
    assert resp.content_type == "application/json"
    ans = await resp.json()

    assert ans["error"]["code"] == -32603
    assert ans["error"]["message"] == "Internal error"
