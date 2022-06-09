import asyncio
import pytest

from aiohttp.pytest_plugin import TestClient
from aiohttp.client import ClientResponse

from .test_utils import jsonrpc_path, create_jsonrpc_request
from .. import App
from ..db.Utils import clear_tables, manager


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


async def test_registration(client: TestClient) -> None:
    response: ClientResponse = await client.post(jsonrpc_path, data=
                                                 create_jsonrpc_request("register",
                                                                        {"username": "Lol",
                                                                         "password": "1234",
                                                                         "email": "lol@pop.me"}))
    dict_response: dict = await response.json()
    assert dict_response["result"] == "ok"


async def test_login(client: TestClient) -> None:
    await client.post(jsonrpc_path,
                      data=create_jsonrpc_request("register",
                                                  {"username": "Lol2",
                                                   "password": "1234",
                                                   "email": "lol@rap.me"}))
    response: ClientResponse = await client.post(jsonrpc_path,
                                                 data=create_jsonrpc_request("login",
                                                                             {"username": "lol2",
                                                                              "password": "1234"}))
    dict_response: dict = await response.json()
    print(dict_response)
    assert not dict_response["result"]["is_admin"]


async def test_user_exists_error(client: TestClient) -> None:
    await client.post(jsonrpc_path,
                      data=create_jsonrpc_request("register",
                                                  {"username": "Lol3",
                                                   "password": "1234",
                                                   "email": "juj@jaj.mu"}))
    response: ClientResponse = await client.post(jsonrpc_path,
                                                 data=create_jsonrpc_request("register",
                                                                             {"username": "lol3",
                                                                              "password": "4321",
                                                                              "email": "olo@uot.tu"}))
    dict_response: dict = await response.json()

    assert dict_response["error"]["code"] == -32000
    assert dict_response["error"]["message"] == "This username or email is already used"


async def test_invalid_email_error(client: TestClient) -> None:
    response: ClientResponse = await client.post(jsonrpc_path,
                                                 data=create_jsonrpc_request("register",
                                                                             {"username": "Lol4",
                                                                              "password": "1234",
                                                                              "email": "aaaaaaa"}))
    dict_response: dict = await response.json()

    assert dict_response["error"]["code"] == -32002
    assert dict_response["error"]["message"] == "Invalid email format"


async def test_wrong_login_error(client: TestClient) -> None:
    await client.post(jsonrpc_path,
                      data=create_jsonrpc_request("register",
                                                  {"username": "Lol5",
                                                   "password": "1234",
                                                   "email": "eyyu@ujuj.ki"}))
    response: ClientResponse = await client.post(jsonrpc_path,
                                                 data=create_jsonrpc_request("login",
                                                                             {"username": "lol5",
                                                                              "password": "1235"}))
    dict_response: dict = await response.json()

    assert dict_response["error"]["code"] == -32001
    assert dict_response["error"]["message"] == "Wrong username or password"


async def test_logout(client: TestClient) -> None:
    await client.post(jsonrpc_path,
                      data=create_jsonrpc_request("register",
                                                  {"username": "Lol6",
                                                   "password": "1234",
                                                   "email": "eyyu43@ujuj.ki"}))
    response: ClientResponse = await client.post(jsonrpc_path,
                                                 data=create_jsonrpc_request("logout", {}))
    dict_response: dict = await response.json()

    assert dict_response["result"] == "ok"


async def test_no_user_logged_in_error(client: TestClient) -> None:
    response = await client.post(jsonrpc_path,
                                 data=create_jsonrpc_request("logout", {}))
    dict_response: dict = await response.json()

    assert dict_response["error"]["code"] == -32003
    assert dict_response["error"]["message"] == "No user is logged in"
