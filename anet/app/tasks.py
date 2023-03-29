import asyncio

from aiohttp import ClientSession

news = ['fb.com']
email = ['ii1', 'ii2', ]
interval = 4

sem = asyncio.Semaphore(5)


async def _worker(url):
    print('start pars')
    await asyncio.sleep(2)
    async with sem:
        await asyncio.sleep(2)
    print(url, 'end parse')


async def parser(app):
    loop = asyncio.get_running_loop()
    event = asyncio.Event()

    async def _looper():
        while True:
            loop.call_later(interval, lambda e: e.set(), event)
            await event.wait()
            await asyncio.gather(*[_worker(n) for n in news])
            event.clear()

    task = asyncio.create_task(_looper(news))
    yield
    await task
    print(task.result())


async def sender(app):
    ...
