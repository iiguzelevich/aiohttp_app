import json
import smtplib
import os
import jwt
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiohttp import web
from tortoise.exceptions import DoesNotExist

from anet.permissions import Simple, Staff, Admin
from anet.utils.crypto import Enigma
from anet.api.user.models import User
from email.mime.text import MIMEText

load_dotenv()


class Serializer(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


class UserView(web.View):
    async def get(self):
        data = await self.request.json()
        user = await User.get(username=data['username']).values(
            'id', 'username', 'email', 'created', 'status'
        )
        return web.json_response(
            {'result': user},
            status=200,
            dumps=lambda v: json.dumps(v, cls=Serializer),
        )

    async def post(self):
        data = await self.request.json()
        new_user = await User.create(**data)
        user_email = data['email']
        user_id = await User.get(
            username=data['username']
        ).values('id')
        user_id = user_id.get('id')

        sender = user_email
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = sender
        msg['Subject'] = 'Activate'
        body = (
            f"127.0.0.1:9001/activate/act?param={user_id}"
        )
        msg.attach(MIMEText(body, 'plain'))
        psswd = os.getenv('PSSWD')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, psswd)
        text = msg.as_string()
        server.sendmail(sender, sender, text)
        return web.json_response({'result': f'{new_user.id}'}, status=200)

    async def put(self):
        data = await self.request.json()
        if isinstance(data, dict):
            user = await User.filter(
                username=data.pop('username')
            ).update(**data)

        elif isinstance(data, list):
            u_name = [el['username'] for el in data]
            users = await User.filter(username__in=u_name)
            for rec, usr in zip(data, users):
                rec.pop('username')
                await usr.update_from_dict(rec)
                await usr.save(update_fields=list(rec.keys()))
        return web.json_response({'result': 'text'}, status=200)

    async def delete(self):
        data = await self.request.json()
        user = await User.get(username=data['username'])
        await user.delete()
        return web.json_response(
            {'result': f'User:{user.id=} was deleted'},
            status=200
        )


class AccessView(web.View):
    async def post(self):
        data = await self.request.json()
        refresh = data.get('refresh', None)

        try:
            alg = jwt.get_unverified_header(refresh)['alg']
        except (jwt.exceptions.InvalidTokenError, KeyError):
            return web.json_response({'message': 'Invalid data'}, status=401)

        try:
            payload = jwt.decode(
                refresh,
                Enigma.public_key,
                algorithms=[alg],
                issuer='refresh',
            )
        except jwt.InvalidIssuerError:
            return web.json_response({'message': 'Invalid issuer'}, status=401)
        except jwt.ExpiredSignatureError:
            return web.json_response({'message': 'Expire error'}, status=401)

        user = await User.get(username=payload['user'])
        if refresh != user.refresh:
            raise web.HTTPNotFound
        time_stamp = datetime.now()
        access_payload = {
            'user': user.username,
            'exp': time_stamp + timedelta(days=5),
            'iss': 'access',
            'iat': time_stamp,
            'aud': user.status.name
        }

        access_token = jwt.encode(
            access_payload,
            Enigma.private_key,
            algorithm='RS256',
            headers={'alg': 'RS256'}
        )

        return web.json_response({'access': access_token}, status=201)


class AuthView(web.View):
    async def post(self):
        data = await self.request.json()

        try:
            user = await User.get(username=data['username'])
        except DoesNotExist:
            return web.json_response(
                {'message': f'User: {data["username"]} not found'},
                status=404
            )

        if await user.check_password(data['password']):
            time_stamp = datetime.now()
            payload = {
                'user': user.username,
                'exp': time_stamp + timedelta(days=5),
                'iss': 'refresh',
            }
            expire = (
                    int((time_stamp + timedelta(days=5)).timestamp()) -
                    int(time_stamp.timestamp())
            )

            refresh_token = jwt.encode(
                payload,
                Enigma.private_key,
                algorithm='RS256',
                headers={'alg': 'RS256'},
            )
            user.refresh = refresh_token
            await user.save(update_fields=['refresh'])

            return web.json_response(
                {'refresh': refresh_token, 'expire': expire},
                status=201
            )
        return web.json_response(
            {'message': f'User: {data["username"]} not found'},
            status=404
        )


@Simple()
class PostView(web.View):
    async def get(self):
        print(await self.request.json())
        return web.json_response({'Info': 'get'}, status=200)

    async def post(self):
        print(await self.request.json())
        return web.json_response({'Info': 'post'}, status=201)

    async def put(self):
        print(await self.request.json())
        return web.json_response({'Info': 'put'}, status=200)

    async def delete(self):
        print(await self.request.json())
        return web.json_response({'Info': 'delete'}, status=200)


@Staff()
class InfoView(web.View):
    async def get(self):
        print(await self.request.json())
        return web.json_response({'Info': 'get'}, status=200)

    async def post(self):
        print(await self.request.json())
        return web.json_response({'Info': 'post'}, status=201)

    @Simple.subpermission
    async def put(self):
        print(await self.request.json())
        return web.json_response({'Info': 'put'}, status=200)

    @Simple.subpermission
    async def delete(self):
        print(await self.request.json())
        return web.json_response({'Info': 'delete'}, status=200)
