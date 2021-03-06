import uuid
from datetime import datetime

import peewee
from aiohttp.web import Request
from aiohttp.web_response import Response, json_response
from aiohttp_security import remember, forget, authorized_userid, permits
from src.db.Models import User, Auction, Bet
from passlib.hash import sha256_crypt

from .Decorators import disabled, requires_login, admin_only, for_tests_only
from .Errors import user_exists_error, wrong_login_error, \
    invalid_email_error, no_user_logged_in_error, auction_does_not_exist_error, auction_is_ongoing_error, \
    auction_has_ended_error, can_not_place_bet_error, auction_has_no_winner_error
from .Utils import make_jsonrpc_response, is_valid_email, make_dict_auction
from src.auth.AuthorizationPolicy import check_credentials


@for_tests_only
async def test(request: Request, json: dict) -> Response:
    b = json["params"]["a"]
    return make_jsonrpc_response(json, "ok")


@for_tests_only
async def internal_error(request: Request, json: dict) -> Response:
    raise ArithmeticError()


async def register(request: Request, json: dict) -> Response:
    params = json["params"]
    username: str = params["username"].lower()
    password = sha256_crypt.hash(params["password"])
    email = params["email"].lower()

    try:
        user = await request.app["db"].get(User.select().where(User.username == username)
                                           .orwhere(User.email == email))
    except peewee.DoesNotExist:
        user = None
    if user:
        return json_response(user_exists_error(json))
    if not is_valid_email(email):
        return json_response(invalid_email_error(json))

    await request.app["db"].create(User, username=username, password=password, email=email)
    response = make_jsonrpc_response(json, "ok")
    await remember(request, response, username)

    return response


async def login(request: Request, json: dict) -> Response:
    params = json["params"]
    username = params["username"].lower()

    if await check_credentials(username, params["password"]):
        response = make_jsonrpc_response(json, {"is_admin": (await request.app["db"]
                                         .get(User.select(User.is_superuser).where(User.username == username)))
                                         .is_superuser})

        await remember(request, response, username)
        return response

    return json_response(wrong_login_error(json))


async def logout(request: Request, json: dict) -> Response:
    user = await authorized_userid(request)

    if not user:
        return json_response(no_user_logged_in_error(json))

    response = make_jsonrpc_response(json, "ok")

    await forget(request, response)
    return response


@admin_only
async def add_item(request: Request, json: dict) -> Response:
    params = json["params"]
    name = params["name"]
    starting_price = params["starting_price"]
    picture = params["picture"]
    description = params["description"]
    end_of_auction = datetime.fromisoformat(params["end_of_auction"])
    id = uuid.uuid4()

    await request.app["db"].create(Auction, id=id, name=name, picture=picture,
                                   description=description, end_of_auction=end_of_auction,
                                   user=await authorized_userid(request), staring_price=starting_price)

    response = make_jsonrpc_response(json, "ok")

    return response


@admin_only
async def change_item_status(request: Request, json: dict) -> Response:
    params = json["params"]
    auction_id = params["id"]

    try:
        auction = await request.app["db"].get(Auction, id=auction_id)
    except (peewee.DoesNotExist, peewee.DataError):
        return json_response(auction_does_not_exist_error(json))
    auction.allowed = False
    await request.app["db"].update(auction)

    response = make_jsonrpc_response(json, "ok")

    return response


@requires_login
async def get_items(request: Request, json: dict) -> Response:
    if await permits(request, "admin"):
        db_items = await request.app["db"].execute(Auction.select().order_by(Auction.end_of_auction))
    else:
        db_items = await request.app["db"].execute(Auction.select()
                                                   .where(Auction.allowed & (Auction.end_of_auction > datetime.now()))
                                                   .order_by(Auction.end_of_auction))

    items = []
    for item in db_items:
        it = make_dict_auction(item)
        it.pop("description")
        it["id"] = str(item.id)
        items.append(it)

    response = make_jsonrpc_response(json, items)

    return response


@requires_login
async def get_item(request: Request, json: dict) -> Response:
    item_id = json["params"]["id"]
    try:
        item: Auction = await request.app["db"].get(Auction, id=item_id)
    except (peewee.DoesNotExist, peewee.DataError):
        return json_response(auction_does_not_exist_error(json))

    result = make_dict_auction(item)
    result["allowed"] = item.allowed
    response = make_jsonrpc_response(json, result)

    return response


@requires_login
async def bet(request: Request, json: dict) -> Response:
    item_id = json["params"]["id"]
    price = float(json["params"]["price"])
    user = await authorized_userid(request)

    try:
        auction = await request.app["db"].get(Auction, id=item_id)
    except (peewee.DoesNotExist, peewee.DataError):
        return json_response(auction_does_not_exist_error(json))

    if not auction.allowed or auction.end_of_auction <= datetime.now():
        return json_response(auction_has_ended_error(json))

    try:
        bet = (await request.app["db"].execute(Bet.select(Bet.bet)
                                               .where(Bet.auction == item_id)
                                               .order_by(Bet.bet.desc())))[0].bet
    except IndexError:
        bet = auction.staring_price

    if price < bet:
        return json_response(can_not_place_bet_error(json))

    await request.app["db"].get_or_create(Bet, auction=item_id, user=user, bet=price)

    response = make_jsonrpc_response(json, "ok")

    return response


@requires_login
async def get_auction_bets(request: Request, json: dict) -> Response:
    item_id = json["params"]["id"]

    try:
        auction: Auction = await request.app["db"].get(Auction.select().where(Auction.id == item_id))
    except (peewee.DoesNotExist, peewee.DataError):
        return json_response(auction_does_not_exist_error(json))

    bets = []
    for bet in await request.app["db"].execute(auction.bets.order_by(Bet.bet.desc())):
        bets.append({
            "username": bet.user.username,
            "price": float(bet.bet)
        })

    return make_jsonrpc_response(json, bets)


@requires_login
async def get_user_bets(request: Request, json: dict) -> Response:
    user = await authorized_userid(request)
    bets = []

    for bet in await request.app["db"].execute(Bet.select().where(Bet.user == user)
                                                           .order_by(Bet.auction, Bet.bet.desc())):
        bets.append({
            "name": bet.auction.name,
            "auction": str(bet.auction.id),
            "price": float(bet.bet)
        })

    return make_jsonrpc_response(json, bets)


@requires_login
async def get_auction_winner(request: Request, json: dict) -> Response:
    item_id = json["params"]["id"]

    try:
        auction = await request.app["db"].get(Auction, id=item_id)
    except (peewee.DoesNotExist, peewee.DataError):
        return json_response(auction_does_not_exist_error(json))

    if auction.allowed and auction.end_of_auction > datetime.now():
        return json_response(auction_is_ongoing_error(json))

    try:
        bet: Bet = (await request.app["db"].execute(auction.bets.order_by(Bet.bet.desc())))[0]
    except IndexError:
        return json_response(auction_has_no_winner_error(json))

    return make_jsonrpc_response(json, bet.user.username)


async def get_user_info(request: Request, json: dict) -> Response:
    user = await authorized_userid(request)

    if not user:
        return json_response(no_user_logged_in_error(json))

    info: User = await request.app["db"].get(User, username=user)

    return make_jsonrpc_response(json, {
        "username": user,
        "email": info.email,
        "is_admin": info.is_superuser
    })
