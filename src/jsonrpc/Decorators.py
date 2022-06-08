import sys

from typing import Callable, Literal
from aiohttp.web import Request
from aiohttp.web_response import Response, json_response
from aiohttp_security import permits

from .Errors import no_access_error, method_disabled_error, method_not_found_error


def disabled(method: Callable):
    async def wrapper(request: Request, json: dict) -> Response:
        return json_response(method_disabled_error(json))
    return wrapper


def requires_login(method: Callable):
    return requires_access_level("public")(method)


def admin_only(method: Callable):
    return requires_access_level("admin")(method)


def requires_access_level(level: Literal["public", "admin"]):
    def requires_access(method: Callable):
        async def wrapper(request: Request, json: dict) -> Response:
            if not await permits(request, level):
                return json_response(no_access_error(json))
            return await method(request, json)
        return wrapper
    return requires_access


def for_tests_only(method: Callable):
    async def wrapper(request: Request, json: dict) -> Response:
        if "pytest" in sys.modules:
            return await method(request, json)
        return json_response(method_not_found_error(json))
    return wrapper
