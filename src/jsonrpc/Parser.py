from aiohttp.web import Request
from json import JSONDecodeError

from aiohttp.web_response import json_response, Response

from . import Methods
from .Errors import parse_error, internal_error, \
    invalid_params_error, invalid_request_error, \
    method_not_found_error


async def parse_jsonrpc(request: Request) -> Response:
    try:
        json: [dict, list] = await request.json()
    except JSONDecodeError:
        return json_response(parse_error())

    try:
        if json["jsonrpc"] != "2.0" or type(json["method"]) is not str\
                or type(json["id"]) is not int:
            raise ValueError
    except (KeyError, ValueError):
        return json_response(invalid_request_error())

    if json is list:
        responses = []

        for call in json:
            responses.append(await method_handler(request, call))

        return json_response(responses)

    return await method_handler(request, json)


async def method_handler(request: Request, json: dict) -> Response:
    try:
        return await getattr(Methods, json["method"])(request, json)
    except AttributeError:
        return json_response(method_not_found_error(json))
    except KeyError:
        return json_response(invalid_params_error(json))
    except Exception as e:
        print(e)
        return json_response(internal_error(json))

