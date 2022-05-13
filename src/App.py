import os

from aiohttp.web import run_app, Application, \
    Request, Response, RouteTableDef
from aiohttp_security import setup as security_setup
from aiohttp_security.session_identity import SessionIdentityPolicy
from aiohttp_session import setup
from aiohttp_session.redis_storage import RedisStorage
from aioredis import Redis

from Utils import manager
from auth.AuthorizationPolicy import AuthorizationPolicy
from jsonrpc import Parser
from src.Models import create_tables

routes = RouteTableDef()


def init() -> Application:
    app = Application()
    app.router.add_routes(routes)
    app["redis"] = Redis(host="redis", password=os.getenv("REDIS_PASS"))
    app["db_manager"] = manager
    setup(app, RedisStorage(app["redis"]))
    security_setup(app, SessionIdentityPolicy(), AuthorizationPolicy())

    create_tables()

    return app


@routes.get("/health")
async def health_check(request: Request) -> Response:
    return Response(status=200)


@routes.post("/api/v1/jsonrpc")
async def jsonrpc_api(request: Request) -> Response:
    return await Parser.parse_jsonrpc(request)


if __name__ == "__main__":
    run_app(init())
