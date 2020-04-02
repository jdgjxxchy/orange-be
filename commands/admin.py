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
from config import BASE_DIR
from main import db

import asyncio

async def addTime(context):
    msg = context['message'].replace('续费', '').strip()
    a = msg.split(' ')
    groupNumber = a[0]
    days = int(a[1])
    group = Group().getByGroup(groupNumber)

    if not group:
        now = datetime.date.today() + datetime.timedelta(days=days)
        Group(group=groupNumber, name=groupNumber, expire=now, robot=context['user_id']).add()
    else:
        now = group.expire + datetime.timedelta(days=days)
        group.expire = now
        group.save()
    return f"续费成功, {groupNumber} 群已续费到{now}"

async def setHongAdmin(context):
    occu, preOccu = find_in_dic(context['message'], occuDic)
    if not occu: return "输入不合法"
    content = context['message'].replace('设置宏', '').replace(preOccu, '', 1).strip()
    return Hong().setHong('0', '0', occu, content) + '\n设置宏成功'

async def exitGroup(context):
    try:
        bot = context['info']['bot']
        a = context['message'].replace('退群', '').strip()
        group = int(a)
        await bot.set_group_leave(self_id=context['self_id'], group_id=group)
        return f"已退出{group}"
    except:
        return "退群失败"


def getDays(info):
    today = datetime.date.today()
    for groupDic in info:
        group = Group().getByGroup(groupDic['group_id'])
        if group:
            days = (group.expire - today).days
            groupDic['days'] = days
        else:
            groupDic['days'] = -1000
    return sorted(info, key=lambda dic: dic['days'], reverse=False)

async def groupAdmin(context):
    if context['user_id'] != 986859110:
        return ''
    bot = context['info']['bot']
    order = context['message'].replace('G', '').strip()
    # 信息
    if order == '信息':
        info = await bot.get_group_list(self_id=context['self_id'])
        res = getDays(info)
        text = ''
        index = 0
        for d in res:
            if d['days'] < 3:
                index += 1
                text += f"{d['group_id']} 剩余天数:{d['days']}\n"
        text += f'群个数: {len(res)}\n即将到期: {index}'
        return text

    # 续费
    elif order == '催费':
        info = await bot.get_group_list(self_id=context['self_id'])
        res = getDays(info)
        reply = ''
        index = 0
        for g in res:
            if g['days'] < 3:
                days = g['days']
                index += 1
                groupNumber = g['group_id']
                reply += f'\n{groupNumber}剩余{days}天'
                s = f'[CQ:image,file=file:///{BASE_DIR}\image\cuifei.png]'
                if days > 0:
                    text = f'{s}\n小橙还有{days}天就要到时间拉'
                elif days == 0:
                    text = f'{s}\n小橙今天结束就要到时间拉'
                else:
                    text = f'{s}\n小橙已经过期{-days}天拉'
                await bot.send_group_msg(self_id=context['self_id'], group_id=groupNumber, message=text)
                await asyncio.sleep(3)
        return f"已催费{index}个群:{reply}"

    elif order.startswith('全部续费'):
        days = int(order.replace('全部续费', '').strip())
        info = await bot.get_group_list(self_id=context['self_id'])
        for each in info:
            group = Group().getByGroup(each['group_id'])
            if group:
                group.expire = group.expire + datetime.timedelta(days=days)
                group.save()
        return "已全部续费"



async def update(context):
    db.session.expire_all()
    return "更新成功"