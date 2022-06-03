import asyncio
import json
import pytest

from aiohttp.pytest_plugin import TestClient

from src import App

jsonrpc_path: str = "/api/v1/jsonrpc"


def create_jsonrpc_request(method: str, params: dict[str, str]) -> str:
    jsonrpc = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

    return json.dumps(jsonrpc, ensure_ascii=False)


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture()
async def client(aiohttp_client) -> TestClient:
    return await aiohttp_client(App.init())
