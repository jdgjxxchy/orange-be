#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: team.py
@time: 2020/1/7

"""

import asyncio
from config import REDIS
from views.urls import handleData, getUser
from quart import websocket, copy_current_websocket_context

import aioredis


async def handle_ws_team(group, bot):
    token = websocket.args.get('token')
    redis = await aioredis.create_redis_pool(REDIS)
    res = await redis.subscribe(f'channel:{group}')
    channel = res[0]

    @copy_current_websocket_context
    async def sending():
        while await channel.wait_message():
            msg = await channel.get(encoding="utf-8")
            await websocket.send(msg)

    @copy_current_websocket_context
    async def receiving():
        while True:
            data = await websocket.receive()
            if (data == 'ping'):
                await websocket.send('pong')
            else:
                user = await getUser(token)
                await handleData(user, bot, data)
            await asyncio.sleep(0)

    try:
        send = asyncio.create_task(sending())
        receive = asyncio.create_task(receiving())
        await asyncio.gather(send, receive)
    finally:
        await redis.unsubscribe(f'channel:{group}')
        redis.close()
        await redis.wait_closed()

