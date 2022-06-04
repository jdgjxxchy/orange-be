#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: query.py
@time: 2020/1/9

"""

import asyncio
import json
import datetime

from models import Hong, Gold
from utils.dicts import occuDic, areaSocketList, areaDict, occuY, yaoDic
from utils.common import find_in_dic, gap
from tortoise.query_utils import Q


# 查宏
@gap('hong', 100)
async def getHong(context):
    group = context['group_id']
    occu, _ = find_in_dic(context['message'], occuDic)
    hong = await Hong.filter(Q(occu=occu), Q(group=group) | Q(group='0')).order_by('-group').all()
    if len(hong) > 0:
        content = hong[0].content.replace('&#91;', '[').replace('&#93;', ']')
        if content == '':
            return ''
        if hong[0].group != '0':
            content += f'\n由本群{hong[0].qq}提供'
        else:
            content += f'\n设置本群专属宏可以使用 设置宏 命令'
        return content + '\n查询宏 群内冷却100秒'
    return ""


# 设置宏
@gap('sethong', 100)
async def setHong(context):
    if context['message'] == "设置宏":
        return "设置本群专属宏的格式为:\n" \
               "设置宏 职业\n" \
               "/cast ...."
    group = context['group_id']
    qq = context['user_id']
    occu, preOccu = find_in_dic(context['message'], occuDic)
    if not occu: return "输入不合法"
    content = context['message'].replace('设置宏', '').replace(preOccu, '', 1).strip()
    if len(content) > 250: return "宏内容太长, 无法设置"
    return await Hong.setHong(qq, group, occu, content) + '\n设置宏 群内冷却100秒'


# 开服监控
@gap('monitor', 300)
async def monitorArea(context):

    area, _ = find_in_dic(context['message'], areaDict)
    if area not in areaSocketList: return ""
    url = areaSocketList[area]
    await context['info']['bot'].send_group_msg(self_id=context['self_id'], group_id=context['group_id'],
                                                message="正在监控! 开服后会在群内at你! 监听模块群内冷却5分钟")

    async def connectTo():
        while 1:
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(url, 3724), 0.2)
                writer.close()
                break
            except:
                await asyncio.sleep(3)

    await connectTo()
    return f'[CQ:at,qq={context["user_id"]}]{area}已经开服啦'

@gap('yao', 100)
async def getYao(context):
    occu , _ = find_in_dic(context['message'], occuDic)
    if occu:
        occuType, _ = find_in_dic(occu, occuY) or find_in_dic(context['message'], occuY)
    else:
        occuType, _ = find_in_dic(context['message'], occuY)
    if occuType:
        return yaoDic[occuType]
    return ""

@gap('gold', 100)
async def getGold(context):
    group = context['info']['group']
    if not group.canGold: return ''
    area, _ = find_in_dic(context['message'], areaDict)
    res = await Gold.get_or_none(area=area)
    if res:
        gold = json.loads(res.gold)
        reply = f'{area}服务器的金价为:\n' \
              f'5173:   {"/".join(map(str, gold["5173"]))}\n' \
              f'万宝阁: {"/".join(map(str, gold["official"]))}\n'
        if len(gold["post"]) > 0:
            reply += f'贴吧:     {"/".join(map(str, gold["post"]))}\n'
        reply += f'更新时间: {res.update_at.strftime("%Y-%m-%d %H:%M:%S")}\n'
        reply += '查询CD100秒'
        return reply


@gap('func', 100)
async def func(context):
    if context['message'] in ['功能', '菜单', '使用说明']:
        return 'QQ小橙是一个专注于排表的PVE机器人.使用说明:\nhttps://www.cnblogs.com/btxlc/p/12419199.html'


@gap('customQA', 100)
async def customQA(context):
    return "!23"


# 剩余时间
async def leftTime(context):
    if context['message'] not in ['剩余时间', '续费']: return ''
    group = context['info']['group']
    expire = group.expire
    left = expire - datetime.date.today()
    return f'本群小橙到期时间为{expire}, 还剩{left.days}天到期'