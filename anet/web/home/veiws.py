from aiohttp import web
from aiohttp_jinja2 import template
from anet.api.user.models import User


class HomePage(web.View):
    @template('home.html')
    async def get(self):
        print(self.request.headers)
        return {'key': 'INFO'}


class Activate(web.View):
    @template('activate.html')
    async def get(self):
        url = self.request.url
        data = (str(url).split('?')[1]).split('=')
        activate_id = int(data[1])
        activate = await User.get(
            id=activate_id
        ).values('is_active')

        if activate['is_active'] is True:
            return {'key': 'You are already activated'}
        else:
            activate = await User.filter(
                id=activate_id
            ).update(is_active=True)
            return {'key': 'Activation was successful'}
