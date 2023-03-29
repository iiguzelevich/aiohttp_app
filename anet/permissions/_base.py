import jwt
from functools import wraps
from typing import TypeAlias
from aiohttp import web
from anet.api.user.models import User
from anet.utils.crypto import Enigma

Request: TypeAlias = web.Request
View: TypeAlias = web.View


class AnonymousUser:
    username = None
    is_anonymous = True


class AbstractPermission :
    perms: list = None

    def __call__(self, handler):
        for meth_name in ('get', 'post', 'put', 'delete'):
            meth = getattr(handler, meth_name)
            if meth is not None:
                setattr(handler, meth_name, self.subpermission(meth))
        return handler

    @classmethod
    def get_token(cls, request: Request):
        try:
            schema, token = request.headers['Authorization'].split(' ')
        except KeyError:
            raise PermissionError('Required "Authorization" header.')
        except ValueError:
            raise PermissionError('Required token schema.')
        if schema != 'Bearer':
            raise PermissionError('Invalid token schema')
        return token

    async def process_token(self, request: web.Request):
        if self.perms is not None:
            token = self.get_token(request)
            token_headers = jwt.get_unverified_header(token)
            try:
                info = jwt.decode(
                    token,
                    Enigma.public_key,
                    algorithms=[token_headers.get('alg')],
                    issuer='access',
                    audience=self.perms,
                )
            except jwt.exceptions.InvalidAudienceError:
                raise PermissionError('Permission denied')
            except jwt.exceptions.InvalidIssuedAtError:
                raise PermissionError(
                    'Invalid token. Required "access" type.'
                )
            except jwt.exceptions.ExpiredSignatureError:
                raise PermissionError('Invalid token schema')
            
            return await User.get(username=info['user'])
        return AnonymousUser()

    @classmethod
    def subpermission(cls, func):
        @wraps(func)
        async def _wrap(view):
            view.user = await cls.process_token(cls, view.request)
            return await func(view)
        return _wrap
