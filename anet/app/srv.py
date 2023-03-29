import os

import jinja2
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup
from anet import settings
from anet.api.user.views import UserView, AuthView, AccessView, PostView
from anet.web.home.veiws import HomePage, Activate
from tortoise.contrib.aiohttp import register_tortoise
from .middles import check_data, check_info
from anet.utils.crypto import Enigma


def create_app():
    app = web.Application(
        middlewares=(check_data, check_info)
    )
    jinja2_setup(
        app,
        loader=jinja2.FileSystemLoader(
            [
                path / 'templates'
                for path in (settings.BASE_DIR / 'web').iterdir()
                if path.is_dir() and (path / 'templates').exists()
            ]
        )
    )
    app.router.add_route('*', '/', HomePage, name='home_page')
    app.router.add_route('*', '/activate/act', Activate, name='activate')
    app.router.add_route(
        '*',
        '/api/user/account',
        UserView,
        name='user_view'
    )
    app.router.add_route(
        '*',
        '/api/user/auth',
        AuthView,
        name='auth_view'
    )
    app.router.add_route(
        '*',
        '/api/user/access',
        AccessView,
        name='access_view'
    )
    app.router.add_route(
        '*',
        '/api/user/posts',
        PostView,
        name='post_view'
    )
    app.router.add_route(
        '*',
        '/api/user/posts',
        PostView,
        name='info_view'
    )
    try:
        Enigma.load_key(settings.PRIVATE_KEY_PATH, )
    except FileNotFoundError:
        with open(settings.PRIVATE_KEY_PATH, 'w') as key_f:
            key_f.write(Enigma.create_key(2048, os.getenv('KEY_PASS')))
    register_tortoise(app, config=settings.DB_CONFIG, generate_schemas=True)
    return app


async def get_app():
    return create_app()
