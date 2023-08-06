
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web


from winden_proto_app.routes import setup_routes


from config import DefaultConfig



CONFIG = DefaultConfig()



async def init_app(argv=None):

    app = web.Application()

    #app['config'] = get_config(argv)

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('winden_proto_app', 'templates'))

    # create db connection on startup, shutdown on exit
    #app.cleanup_ctx.append(pg_context)

    # setup views and routes
    setup_routes(app)

    #setup_middlewares(app)

    return app


def main(argv):

    app = init_app(argv)

    web.run_app(app,
                host='localhost',
                port=CONFIG.PORT)


if __name__ == '__main__':
    main(sys.argv[1:])