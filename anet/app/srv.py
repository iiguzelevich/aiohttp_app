import jinja2
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup
from anet import settings
from anet.web.home.veiws import HomePage
from tortoise.contrib.aiohttp import register_tortoise


def create_app():
    app = web.Application()
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
    app.router.add_route('GET', '/', HomePage, name='home_page')
    register_tortoise(app, config=settings.DB_CONFIG, generate_schemas=True)
    return app


async def get_app():
    return create_app()
