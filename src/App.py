import logging
import os

from aiohttp.web import run_app, Application, \
    Request, Response
from aioredis import from_url


def init() -> Application:
    app = Application()
    app.router.add_route("GET", "/health", healthcheck)
    app["red"] = from_url("redis://default:4B*Phw7KMV@redis:6379/1")

    return app


async def healthcheck(request: Request) -> Response:
    await request.app["red"].rpush("a", 33)
    return Response(status=200)


if __name__ == "__main__":
    run_app(init())
