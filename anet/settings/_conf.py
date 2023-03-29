import pathlib
import os
from dotenv import load_dotenv

__all__ = ('BASE_DIR', 'DB_CONFIG', 'PRIVATE_KEY_PATH')

BASE_DIR = pathlib.Path(__file__).parent.parent.absolute()

load_dotenv()

mysql_conn = os.getenv("MYSQL_CONN")

DB_CONFIG = {
    'connections': {
        'default': f'mysql://{mysql_conn}'
    },
    'apps': {
        'user': {
            'models': ["anet.api.user.models"],
            'default_connection': 'default',
        }
    },
    'use_tz': True,
    'timezone': 'UTC',
}
PRIVATE_KEY_PATH = BASE_DIR / 'private.pem'
