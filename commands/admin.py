#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: admin.py
@time: 2020/1/10

"""

import datetime
from models import Group, Hong
from utils.common import find_in_dic
from utils.dicts import occuDic


async def addTime(context):
    msg = context['message'].replace('续费', '').strip()
    a = msg.split(' ')
    groupNumber = a[0]
    days = int(a[1])
    group = await Group.get_or_none(group=groupNumber)

    if not group:
        now = datetime.date.today() + datetime.timedelta(days=days)
        await Group.create(group=groupNumber, name=groupNumber, expire=now, robot=context['user_id'])
    else:
        now = datetime.date.today()
        if now > group.expire: group.expire = now
        now = group.expire = group.expire + datetime.timedelta(days=days)
        await group.save()
    return f"续费成功, {groupNumber} 群已续费到{now}"


async def setHongAdmin(context):
    occu, preOccu = find_in_dic(context['message'], occuDic)
    if not occu: return "输入不合法"
    content = context['message'].replace('设置宏', '').replace(preOccu, '', 1).strip()

    return await Hong.setHong('0', '0', occu, content) + '\n设置宏成功'

async def exitGroup(context):
    try:
        bot = context['info']['bot']
        a = context['message'].replace('退群', '').strip()
        group = int(a)
        await bot.set_group_leave(self_id=context['self_id'], group_id=group)
        return f"已退出{group}"
    except:
        return "退群失败"


async def restart(context):
    bot = context['info']['bot']
    await bot.set_restart_plugin(delay=1000)
    return "重启成功"