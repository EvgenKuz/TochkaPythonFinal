import uuid
from datetime import datetime

import peewee
from aiohttp.web import Request
from aiohttp.web_response import Response, json_response
from aiohttp_security import remember, forget, authorized_userid, permits
from src.db.Models import User, Auction, Bet
from passlib.hash import sha256_crypt

from .Errors import user_exists_error, wrong_login_error, \
    invalid_email_error, no_user_logged_in_error, no_access_error, method_disabled_error
from .Utils import make_jsonrpc_response, is_valid_email
from src.Utils import manager
from src.auth.AuthorizationPolicy import check_credentials


async def test(request: Request, json: dict) -> Response:
    b = json["params"]["a"]
    json = {"jsonrpc": "2.0", "result": "ok", "id": json["id"]}
    return json_response(json)


async def internal_error(request: Request, json: dict) -> Response:
    raise ArithmeticError()


async def register(request: Request, json: dict) -> Response:
    params = json["params"]
    username: str = params["username"].lower()
    password = sha256_crypt.hash(params["password"])
    email = params["email"].lower()

    try:
        user = await manager.get(User.select().where(User.username == username)
                                     .orwhere(User.email == email))
    except peewee.DoesNotExist:
        user = None
    if user:
        return json_response(user_exists_error(json))
    if not is_valid_email(email):
        return json_response(invalid_email_error(json))

    await manager.create(User, username=username, password=password, email=email)
    response = make_jsonrpc_response(json["id"])
    response["result"] = "ok"
    response = json_response(response)
    await remember(request, response, username)

    return response


async def login(request: Request, json: dict) -> Response:
    params = json["params"]
    username = params["username"].lower()

    if await check_credentials(username, params["password"]):
        response = make_jsonrpc_response(json["id"])
        response["result"] = "ok"
        response = json_response(response)

        await remember(request, response, username)
        return response

    return json_response(wrong_login_error(json))


async def logout(request: Request, json: dict) -> Response:
    user = await authorized_userid(request)

    if not user:
        return json_response(no_user_logged_in_error(json))

    response = make_jsonrpc_response(json["id"])
    response["result"] = "ok"
    response = json_response(response)

    await forget(request, response)
    return response


async def add_item(request: Request, json: dict) -> Response:
    if not await permits(request, "admin"):
        return json_response(no_access_error(json))

    params = json["params"]
    name = params["name"]
    starting_price = params["starting_price"]
    picture = params["picture"]
    description = params["description"]
    end_of_auction = datetime.fromisoformat(params["end_of_auction"])
    id = uuid.uuid4()

    await manager.create(Auction, id=id, name=name, picture=picture,
                         description=description, end_of_auction=end_of_auction, user=await authorized_userid(request),
                         staring_price=starting_price)

    response = make_jsonrpc_response(json["id"])
    response["result"] = "ok"
    response = json_response(response)

    return response


async def change_item_status(request: Request, json: dict) -> Response:
    return json_response(method_disabled_error(json))
    if not await permits(request, "admin"):
        return json_response(no_access_error(json))

    params = json["params"]
    auction_id = params["id"]
    allowed = params["allowed"]

    auction = await manager.get(Auction, id=auction_id)
    auction.allowed = allowed
    await manager.update(auction)

    response = make_jsonrpc_response(json["id"])
    response["result"] = "ok"
    response = json_response(response)

    return response


async def get_items(request: Request, json: dict) -> Response:
    if not await permits(request, "public"):
        return json_response(no_access_error(json))

    db_items: list[Auction] = []
    if await permits(request, "admin"):
        db_items = await manager.execute(Auction.select().order_by(Auction.end_of_auction))
    else:
        db_items = await manager.execute(Auction.select().where(Auction.allowed).order_by(Auction.end_of_auction))

    items = []
    for item in db_items:
        items.append({
            "id": str(item.id),
            "name": item.name,
            "starting_price": float(item.staring_price),
            "picture": item.picture,
            "end_of_auction": item.end_of_auction.isoformat()
        })

    response = make_jsonrpc_response(json["id"])
    response["result"] = items
    response = json_response(response)

    return response


async def get_item(request: Request, json: dict) -> Response:
    if not await permits(request, "public"):
        return json_response(no_access_error(json))

    item_id = json["params"]["id"]
    item: Auction = await manager.get(Auction, id=item_id)

    response = make_jsonrpc_response(json["id"])
    response["result"] = {
        "name": item.name,
        "starting_price": float(item.staring_price),
        "picture": item.picture,
        "description": item.description,
        "end_of_auction": item.end_of_auction.isoformat()
    }
    response = json_response(response)

    return response


async def bet(request: Request, json: dict) -> Response:
    if not await permits(request, "public"):
        return json_response(no_access_error(json))

    item_id = json["params"]["id"]
    price = json["params"]["price"]
    user = await authorized_userid(request)

    try:
        await manager.get(Bet.select().where(Bet.auction == item_id, Bet.user == user, Bet.bet == price))
    except peewee.DoesNotExist:
        await manager.create(Bet, auction=item_id, user=user, bet=price)

    response = make_jsonrpc_response(json["id"])
    response["result"] = "ok"

    return json_response(response)
