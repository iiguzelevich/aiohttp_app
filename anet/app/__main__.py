from .srv import create_app
from aiohttp import web


try:
    web.run_app(create_app(), host='127.0.0.1', port=9001)
except KeyboardInterrupt:
    print('\rStop')
