#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: main.py
@time: 2020/1/7

"""
from flask_sqlalchemy import SQLAlchemy
from aiocqhttp import CQHttp
from config import BaseConfig, REDIS
from sanic_cors import CORS
from utils.Request import Request

import aioredis
import asyncio
import time

bot = CQHttp(enable_http_post=False)
CORS(bot.server_app)
bot.server_app.config.from_object(BaseConfig)
db = SQLAlchemy(bot.server_app)

@bot.server_app.listener("after_server_start")
async def init(app):
    from utils.common import saveGold
    bot.req = Request()
    bot.redis = await aioredis.create_redis_pool(REDIS)
    asyncio.ensure_future(saveGold(bot.req))

@bot.on_message('group')
async def handle_group_msg(context):
    from commands.url import parse_group
    context['info'] = { "bot" :bot }
    # now = time.time()
    reply = await parse_group(context)
    # print(time.time() - now)
    if reply:
        del context['info']
        # print(reply)
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
            "如果要引入我或者提交bug请加群716860454"
    await bot.set_friend_add_request(self_id=context['self_id'], flag=context['flag'], approve=True)
    await bot.send(context, message=reply)

@bot.on_request('group')
async def handle_group_request(context):
    from commands.url import handle_request
    context['bot'] = bot
    await handle_request(context)


@bot.server_app.websocket('/team/<group>')
async def on_ws_team(group):
    from views.team import handle_ws_team
    await handle_ws_team(group, bot)

@bot.server_app.route('/http/<command>')
async def on_handle_index(request, command):
    from views.urls import handle_http
    token = request.headers.get("token")
    return await handle_http(command, bot, token)

@bot.server_app.route('/login', methods=['POST'])
async def handle_login(request):
    from views.urls import login
    form = await request.get_json()
    return await login(form['username'], form["password"], form["groupNumber"])

if __name__ == '__main__':
    bot.run(host='127.0.0.1', port=9876, use_reloader=False)