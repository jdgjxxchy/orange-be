#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: test.py
@time: 2020/1/7

"""

# import asyncio
# import websockets
# import time
#
# async def hello(websocket, path):
#     print(time.time())
#     print(123)
#     while True:
#         try:
#             s = await websocket.recv()
#             print(s)
#         except asyncio.exceptions.CancelledError as e:
#             print(e)
#
#
# start_server = websockets.serve(hello, "localhost", 8765)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
#
# from aiohttp import web
# import aiohttp
#
# app = web.Application()
#
#
# async def websocket_handler(request):
#
#     ws = web.WebSocketResponse()
#     await ws.prepare(request)
#
#     async for msg in ws:
#         print(msg, msg.type, msg.data)
#         if msg.type == aiohttp.WSMsgType.TEXT:
#             if msg.data == 'close':
#                 await ws.close()
#         elif msg.type == aiohttp.WSMsgType.ERROR:
#             print('ws connection closed with exception %s' %
#                   ws.exception())
#
#     print('websocket connection closed')
#
#     return ws
#
# app.add_routes([web.get('/', websocket_handler)])
#
# web.run_app(app, port=8765)

from tortoise import Tortoise, fields, run_async
from models import User, Group
import datetime
from tortoise.functions import Avg, Count, Sum





async def delete_repeat():
    users = await User.annotate(count=Count('id')).group_by('qq', 'group_id')\
        .filter(count__gt=1)\
        .values("qq", "group_id", "count")
    print(users)
    for user in users:
        u = await User.filter(qq=user['qq'], group_id=user['group_id']).all()
        print(u)
        for s in u[1:]:
            await s.delete()


async def delete_expire():
    groups = await Group.all()
    for group in groups:
        now = datetime.date.today() - datetime.timedelta(days=2)
        if now > group.expire:
            async for user in group.users:
                await user.delete()
            async for team in group.teams:
                await team.delete()
            async for tem in group.templates:
                await tem.delete()
            print(group.group + '已清理')
            await group.delete()


async def run():
    await Tortoise.init(
        # db_url="mysql://root:jdgjxxchy_0820@localhost:3306/orange",
        db_url="mysql://root:Hpxt2020hpxt!@47.101.173.121:3306/orange",
        modules={"models": ["models"]},
    )

    await delete_repeat()
    await delete_expire()

if __name__ == "__main__":
    run_async(run())