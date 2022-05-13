import peewee
from aiohttp.web import Request
from aiohttp.web_response import Response, json_response
from aiohttp_security import remember, forget, authorized_userid
from src.Models import User
from passlib.hash import sha256_crypt
from .Errors import user_exists_error, wrong_login_error, \
    invalid_email_error, no_user_logged_in_error
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
