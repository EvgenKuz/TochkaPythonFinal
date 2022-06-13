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
    return asyncio.new_event_loop()


@pytest.fixture()
async def client(aiohttp_client) -> TestClient:
    return await aiohttp_client(App.init())


async def test_add_item(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester",
        "password": "1234",
        "email": "123@mail.com"
    }))
    await make_admin("tester")
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item1",
        "starting_price": 10,
        "picture": "https://img3.wikia.nocookie.net/__cb20140520032019/mariokart/images/f/fc/ItemBoxMK8.png",
        "description": "A thing",
        "end_of_auction": "2023-01-23T01:23:45.678+05:00"
    }))

    assert (await resp.json())["result"] == "ok"


async def test_add_item_no_access(client: TestClient) -> None:
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item2",
        "starting_price": 10.4,
        "picture": "blablalink",
        "description": "A thing 2",
        "end_of_auction": "2023-02-23T01:23:45.678"
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_change_item_status(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester2",
        "password": "1234",
        "email": "yui@mui.dui"
    }))
    await make_admin("tester2")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item3",
        "starting_price": 12.4,
        "picture": "blablalink2",
        "description": "A thing 3",
        "end_of_auction": "2023-02-10T01:23:45.678"
    }))
    item_id: Auction = await manager.get(Auction, Auction.user == "tester2")

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {
        "id": str(item_id.id),
    }))
    ans = await resp.json()

    assert ans["result"] == "ok"


async def test_change_item_status_auction_does_not_exist(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester2.1",
        "password": "1234",
        "email": "yui@muuuui.dui"
    }))
    await make_admin("tester2.1")

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {
        "id": "huhuh"
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32006
    assert ans["error"]["message"] == "Auction with this id doesn't exist"


async def test_change_item_status_no_access(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester3",
        "password": "1234",
        "email": "yui@mui.dut"
    }))
    await make_admin("tester3")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item4",
        "starting_price": 15.45,
        "picture": "blablalink3",
        "description": "A thing 4",
        "end_of_auction": "2023-02-12T01:23:45.678"
    }))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester3.1",
        "password": "1234",
        "email": "yui@mut.dut"
    }))

    item_id: Auction = await manager.get(Auction, Auction.user == "tester3")
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {
        "id": str(item_id.id),
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_get_items_user(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester4",
        "password": "1234",
        "email": "tui@mui.dut"
    }))
    await make_admin("tester4")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item5",
        "starting_price": 25.45,
        "picture": "blablalink4",
        "description": "A thing 5",
        "end_of_auction": "2023-03-12T01:23:45+05:00"
    }))
    """item_id: Auction = await manager.get(Auction, Auction.user == "tester4")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {
        "id": str(item_id.id),
        "allowed": True
    }))"""
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester5",
        "password": "1234",
        "email": "afa@faa.fa"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()

    assert type(ans["result"]) == list
    item = {}
    for it in ans["result"]:
        if it["name"] == "Item5":
            item = it
            break
    assert item["starting_price"] == 25.45
    assert item["picture"] == "blablalink4"
    assert item["end_of_auction"] == "2023-03-11T20:23:45"
    assert "id" in item


async def test_get_items_admin(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester6",
        "password": "1234",
        "email": "tud@mud.dut"
    }))
    await make_admin("tester6")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item6",
        "starting_price": 26.55,
        "picture": "blablalink5",
        "description": "A thing 6",
        "end_of_auction": "2019-03-13T01:23:45+05:00"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()

    assert type(ans["result"]) == list
    item = {}
    for it in ans["result"]:
        if it["name"] == "Item6":
            item = it
            break
    assert item["starting_price"] == 26.55
    assert item["picture"] == "blablalink5"
    assert item["end_of_auction"] == "2019-03-12T20:23:45"
    assert "id" in item


async def test_get_items_no_access_error(client: TestClient) -> None:
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_get_item(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester7",
        "password": "1234",
        "email": "tud@muuuuud.dut"
    }))
    await make_admin("tester7")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item7",
        "starting_price": 26.55,
        "picture": "blablalink6",
        "description": "A thing 7",
        "end_of_auction": "2024-03-13T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item7":
            item_id = it["id"]

    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_item", {"id": item_id}))
    ans = (await resp.json())["result"]

    assert ans["name"] == "Item7"
    assert ans["starting_price"] == 26.55
    assert ans["picture"] == "blablalink6"
    assert ans["description"] == "A thing 7"
    assert ans["end_of_auction"] == "2024-03-13T01:23:45"
    assert ans["allowed"]


async def test_get_item_no_access(client: TestClient) -> None:
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_item", {"id": "12345"}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_get_item_auction_does_not_exist_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester7.1",
        "password": "1234",
        "email": "tud@mgd.dut"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_item", {"id": "12454"}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32006
    assert ans["error"]["message"] == "Auction with this id doesn't exist"


async def test_bet(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester8",
        "password": "1234",
        "email": "tud@mud.dat"
    }))
    await make_admin("tester8")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item8",
        "starting_price": 28.55,
        "picture": "blablalink7",
        "description": "A thing 8",
        "end_of_auction": "2024-09-13T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item8":
            item_id = it["id"]

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {
        "id": item_id,
        "price": 45
    }))
    ans = await resp.json()

    assert ans["result"] == "ok"


async def test_bet_no_access(client: TestClient) -> None:
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {
        "id": "455005",
        "price": 40
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_bet_auction_does_not_exist_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester8.1",
        "password": "1234",
        "email": "tud@myd.dat"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {
        "id": "12456",
        "price": 12.4
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32006
    assert ans["error"]["message"] == "Auction with this id doesn't exist"


async def test_bet_auction_ended_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester8.2",
        "password": "1234",
        "email": "tukkkd@mud.dat"
    }))
    await make_admin("tester8.2")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item8.2",
        "starting_price": 28.55,
        "picture": "blablalink7",
        "description": "A thing 8",
        "end_of_auction": "2024-09-13T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item8.2":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("change_item_status", {"id": item_id}))
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {
        "id": item_id,
        "price": 100
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32008
    assert ans["error"]["message"] == "Auction has ended"


async def test_get_auction_bets(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester9",
        "password": "1234",
        "email": "tar@juk.lo"
    }))
    await make_admin("tester9")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item9",
        "starting_price": 28.55,
        "picture": "blablalink8",
        "description": "A thing 9",
        "end_of_auction": "2024-09-13T01:23:45"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item9":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 140}))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 145}))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_bets", {
        "id": item_id
    }))
    ans = (await resp.json())["result"]

    assert type(ans) == list
    assert len(ans) == 2
    assert ans[0]["price"] == 145


async def test_get_auction_bets_no_access_error(client: TestClient) -> None:
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_bets", {
        "id": "2344"
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"


async def test_get_auction_bets_auction_does_not_exist_error(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester9.1",
        "password": "1234",
        "email": "tar@jukk.lo"
    }))

    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_auction_bets", {
        "id": "aaaa2222aaaaaa"
    }))
    ans = await resp.json()

    assert ans["error"]["code"] == -32006
    assert ans["error"]["message"] == "Auction with this id doesn't exist"


async def test_get_user_bets(client: TestClient) -> None:
    await client.post(jsonrpc_path, data=create_jsonrpc_request("register", {
        "username": "tester10",
        "password": "1234",
        "email": "tar@juuk.lo"
    }))
    await make_admin("tester10")
    await client.post(jsonrpc_path, data=create_jsonrpc_request("add_item", {
        "name": "Item10",
        "starting_price": 28.55,
        "picture": "blablalink9",
        "description": "A thing 10",
        "end_of_auction": "2024-09-13T01:23:45"
    }))
    resp: ClientResponse = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_items", {}))
    ans = await resp.json()
    item_id = ""

    for it in ans["result"]:
        if it["name"] == "Item10":
            item_id = it["id"]

    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 142}))
    await client.post(jsonrpc_path, data=create_jsonrpc_request("bet", {"id": item_id, "price": 148}))

    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_user_bets", {}))
    ans = (await resp.json())["result"]

    assert type(ans) == list
    assert len(ans) == 2
    assert ans[0]["name"] == "Item10"
    assert ans[0]["price"] == 148


async def test_get_user_bets_no_access_error(client: TestClient) -> None:
    resp = await client.post(jsonrpc_path, data=create_jsonrpc_request("get_user_bets", {}))
    ans = await resp.json()

    assert ans["error"]["code"] == -32004
    assert ans["error"]["message"] == "You have no access to this method"
