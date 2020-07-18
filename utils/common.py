#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: common.py
@time: 2020/1/9

"""

from models import Gap, Group, User
from views.data import getUserDetail
from utils.get_gold import get_gold
from utils.dicts import areaList

import time
import datetime
import random
import asyncio
import string


def find_in_dic(s, dic):
    for key in dic:
        for i in dic[key]:
            if i in s:
                return key, i
    return None, None

def gap(cmd, sec):
    def foo(func):
        async def bar(context):
            from config import TIMINGDEBUG
            if TIMINGDEBUG:
                return await func(context)
            group = context['group_id']
            last, _ = await Gap.get_or_create({},group=group)
            lastTime = getattr(last, cmd)
            now = time.time()
            if lastTime and now - lastTime < sec:
                return ''
            reply = await func(context)
            if reply and not reply.startswith('**'):
                setattr(last, cmd, now)
                await last.save()
            return reply
        return bar
    return foo

async def preHandle(context):
    from views.handlers import sendData
    group = await Group.get_or_none(group=str(context['group_id']))
    if not group:
        return True
    context['info']['group'] = group
    now = datetime.date.today()
    expire = group.expire
    if now > expire:
        return True
    user = await User.filter(qq=str(context['user_id']), group=group)
    if len(user) == 0:
        if 'card' not in context['sender']:
            return True
        nickname = context['sender']['card'] if context['sender']['card'] else context['sender']['nickname']
        user = await User(qq=context['user_id'], group=group, name='')
        user.name = nickname
        if context['sender']['role'] == 'owner':
            user.auth = '2111'
        elif context['sender']['role'] == 'admin':
            user.auth = '1111'
        try:
            await user.save()
        except:
            user.name = str(context['user_id'])
            await user.save()
        finally:
            await sendData(group.group, context['info']['bot'], getUserDetail(user, 'createUser'))
            context['info']['user'] = user
            return False
    elif len(user) > 1:
        name = ''
        for u in user[1:]:
            name += u.qq + ' '
        name += f'\n查询的条件为 qq={str(context["user_id"])}, group={group.group}'
        await context['info']['bot'].send_private_msg(user_id=986859110, self_id=context['self_id'], message=name)
    context['info']['user'] = user[0]
    return False


def getString(length=10):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


async def saveGold(req):
    while True:
        for area in areaList:
            await get_gold(req, area)
        await asyncio.sleep(20 * 60)
