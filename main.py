#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: main.py
@time: 2020/1/7

"""
from tortoise.contrib.quart import register_tortoise
from aiocqhttp import CQHttp
from quart import request
from config import REDIS
from utils.Request import Request
from quart_cors import route_cors

import aioredis
import asyncio
import time

bot = CQHttp(enable_http_post=False)
bot.logger.setLevel(30)

register_tortoise(
    bot.server_app,
    # db_url="mysql://root:Jdgjxxchy_0820@localhost:3306/orange",
    db_url="mysql://root:Hpxt2020hpxt!@47.101.173.121:3306/orange",
    # db_url="mysql://root:Hpxt2020hpxt!@localhost:3306/orange",
    modules={"models": ["models"]},
    generate_schemas=True,
)

@bot.server_app.before_first_request
async def init():
    from utils.common import saveGold
    bot.req = Request()
    bot.redis = await aioredis.create_redis_pool(REDIS)
    asyncio.ensure_future(saveGold(bot.req))

@bot.on_message('group')
async def handle_group_msg(context):
    from commands.url import parse_group
    context['info'] = { "bot" :bot }
    now = time.time()
    reply = await parse_group(context)
    print(time.time() - now)
    if reply:
        del context['info']
        print(reply)
        try:
            await bot.send(context, message=reply)
            pass
        except:
            print("被禁言了?")

@bot.on_message('private')
async def handle_private_msg(context):
    from commands.url import parse_private
    context['info'] = { "bot" :bot }
    reply = await parse_private(context)
    if reply:
        del context['info']
        await bot.send(context, message=reply)

@bot.on_request('friend')
async def handle_request(context):
    reply = "你好! 我是QQ小橙, 是个团队排表机器人\n" \
            "如果要引入我或者提交bug请加群1154625773"
    await bot.set_friend_add_request(self_id=context['self_id'], flag=context['flag'], approve=True)
    await bot.send(context, message=reply)

@bot.on_request('group')
async def handle_group_request(context):
    from commands.url import handle_request
    context['bot'] = bot
    await handle_request(context)

@bot.on_meta_event('lifecycle.connect')
async def connect_bot(context):
    print(context)
    robot_qq = context['self_id']
    await bot.send_private_msg(user_id=986859110, self_id=robot_qq, message='我连上了')
    await bot.clean_data_dir(data_dir='image')
    await bot.clean_data_dir(data_dir='record')
    await bot.clean_data_dir(data_dir='show')
    await bot.clean_data_dir(data_dir='bface')

@bot.server_app.websocket('/team/<group>')
async def on_ws_team(group):
    from views.team import handle_ws_team
    await handle_ws_team(group, bot)

@bot.server_app.route('/http/<command>', methods=["GET", "OPTIONS"])
@route_cors()
async def on_handle_index(command):
    from views.urls import handle_http
    token = request.headers.get("token")
    return await handle_http(command, bot, token)

@bot.server_app.route('/login', methods=["POST", "OPTIONS"])
@route_cors()
async def handle_login():
    from views.handlers import login
    form = await request.json
    return await login(form['username'], form["password"], form["groupNumber"])

if __name__ == '__main__':

    bot.run(
        host='0.0.0.0',
        port=9999,
        debug=True,
    )