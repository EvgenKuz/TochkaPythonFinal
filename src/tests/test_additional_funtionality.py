import asyncio

import pytest

from aiohttp.pytest_plugin import TestClient
from aiohttp.client import ClientResponse

from .test_utils import jsonrpc_path, create_jsonrpc_request
from .. import App
from ..db.Models import Auction
from ..db.Utils import clear_tables, make_admin, manager


@pytest.fixture(scope="module", autouse=True)
async def teardown():
    yield
    clear_tables()
    await manager.close()


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def client(aiohttp_client) -> TestClient:
    return await aiohttp_client(App.init())


async def test_get_auction_winner(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester11",
        "password": "1234",
        "email": "tar@jaaak.lo"
    }))
    await make_admin("tester11")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item11",
        "starting_price": 28.55,
        "picture": "blablalink10",
        "description": "A thing 11",
        "end_of_auction": "2024-09-14T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item11":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 142}))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 148}))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {"id": item_id}))

    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_winner", {"id": item_id}))
    ans = await resp.json()

    assert ans["result"] == "tester11"


async def test_get_auction_winner_auction_is_ongoing_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester11.1",
        "password": "1234",
        "email": "tar@yaaak.lo"
    }))
    await make_admin("tester11.1")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item11.1",
        "starting_price": 28.55,
        "picture": "blablalink10",
        "description": "A thing 11",
        "end_of_auction": "2024-09-14T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item11.1":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 142}))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 148}))

    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_winner", {"id": item_id}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32007
    assert ans["error"]["message"] == "Auction hasn't ended yet"


async def test_get_auction_winner_auction_does_not_exist_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester11.2",
        "password": "1234",
        "email": "tffar@jaaak.lo"
    }))
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_winner", {"id": "hhhahh"}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32006
    assert ans["error"]["message"] == "Auction with this id doesn't exist"


async def test_get_auction_winner_no_access_error(client: TestClient) -> None:
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_winner", {"id": "hhhahh"}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_get_auction_winner_no_winner_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester11.3",
        "password": "1234",
        "email": "tar@ytaaak.lo"
    }))
    await make_admin("tester11.3")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item11.3",
        "starting_price": 28.55,
        "picture": "blablalink10",
        "description": "A thing 11",
        "end_of_auction": "2024-09-14T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item11.3":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {"id": item_id}))
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_winner", {"id": item_id}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32009
    assert ans["error"]["message"] == "Auction has no winner"


async def test_get_user_info(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester12",
        "password": "1234",
        "email": "tfftar@jaaak.lo"
    }))
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_user_info", {}))
    ans = (await resp.json())["result"]

    assert ans["username"] == "tester12"
    assert ans["email"] == "tfftar@jaaak.lo"
    assert not ans["is_admin"]


async def test_get_user_info_no_user_logged_in_error(client: TestClient) -> None:
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_user_info", {}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32003
    assert ans["error"]["message"] == "No user is logged in"
