import os
import logging
import mimetypes

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
    add_routes(app)
    app["redis"] = Redis(host="redis", password=os.getenv("REDIS_PASS"))
    app["db_manager"] = manager
    setup(app, RedisStorage(app["redis"]))
    security_setup(app, SessionIdentityPolicy(), AuthorizationPolicy())

    create_tables()

    logging.basicConfig(level=logging.DEBUG)
    return app


#@routes.get("/")
#async def main(request: Request) -> Response:
#    with open("../front-end/index.html", 'r', encoding="utf-8") as html:
#        return Response(text=html.read(), content_type="text/html")


@routes.get("/health")
async def health_check(request: Request) -> Response:
    return Response(status=200)


@routes.post("/api/v1/jsonrpc")
async def jsonrpc_api(request: Request) -> Response:
    return await Parser.parse_jsonrpc(request)


def add_routes(app: Application):
    mimetypes.init()
    mimetypes.types_map['.js'] = 'application/javascript; charset=utf-8'
    mimetypes.types_map['.vue'] = 'application/javascript; charset=utf-8'

    app.router.add_routes(routes)


if __name__ == "__main__":
    run_app(init())
