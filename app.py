
import sys

import logging
logging.basicConfig(level=logging.WARNING)

import aiohttp_jinja2
import jinja2
from aiohttp import web

from git import Repo


from winden_proto_app.routes import setup_routes
from winden_proto_app.middlewares import setup_middlewares
from winden_proto_app.db import setup_db


from config import DefaultConfig



CONFIG = DefaultConfig()



async def init_app(argv=None):

    app = web.Application()

    #app['config'] = get_config(argv)

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('winden_proto_app', 'templates'))
    
    # check for updates
    #git = Repo(".").git
    #try:
    #    git.fetch()
    #    print(git.status())
    #finally:
    #    print("git fetch concluded")


    # ???
    await setup_db(app)

    # setup views and routes
    setup_routes(app)

    setup_middlewares(app)

    return app


def main(argv):

    app = init_app(argv)

    web.run_app(app,
                host='localhost',
                port=int(CONFIG.PORT))


if __name__ == '__main__':
    main(sys.argv[1:])