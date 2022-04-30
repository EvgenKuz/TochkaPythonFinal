import os

from aiohttp.web import run_app, Application, \
    Request, Response
from aioredis import Redis


def init() -> Application:
    app = Application()
    app.router.add_route("GET", "/health", health_check)
    app["red"] = Redis(host="redis", password=os.getenv("REDIS_PASS"))

    return app


async def health_check(request: Request) -> Response:
    return Response(status=200)


if __name__ == "__main__":
    run_app(init())
