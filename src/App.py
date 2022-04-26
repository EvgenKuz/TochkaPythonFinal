from aiohttp.web import run_app, Application


def init():
    app = Application()

    return app


if __name__ == "__main__":
    run_app(init())
