#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: url.py
@time: 2020/1/9

"""

import re
from commands.query import *
from commands.admin import *
from commands.team import *
from utils.common import preHandle
from commands.other import handle_invite


startswith_group = {

    # 团队排表指令
    '开团': startTeam,
    '取消开团': cancelTeam,
    '取消团队': cancelTeam,
    '删除团队': cancelTeam,
    '删除开团': cancelTeam,
    '查看团队': getTeam,
    '报名': signUp,
    '代报名': signUp,
    '我要报名': signUp,
    '取消报名': cancelSignUp,
    '登记老板': recordClient,
    '查看老板': getClients,
    '取消老板': cancelClient,
    '删除老板': cancelClient,

    '修改昵称': editName,
    '改名': editName,
    '修改团名': editTeamName,
    '设置团队备注': setTip,
    '设置报名权限': setSignAuth,

    #剑三查询指令
    '宏': getHong,
    '设置宏': setHong,
    '小药': getYao,
    '小吃': getYao,
    '金价': getGold,
    # 'roll': roll,
    # '硅石': gui,
    # '瑰石': gui,
    '开服监控': monitorArea,
    '开服': monitorArea,
    # '副本': getFB,
    # '攻略': getFB,

    #管理开关
    # '功能开关' : funcOpen,
    # '开启': start,
    # '关闭': end,
    '功能': func,
    '菜单': func,
    '使用说明': func,
    # '设置问答': setQA,
    # '删除问答': delQA,
    # '自定义问答': getQA,
    '剩余时间': leftTime,
    '续费': leftTime,
}

endswith_group = {
    '宏': getHong,
    '小药': getYao,
    '小吃': getYao,
    '药': getYao,
    '金价': getGold,
}



async def parse_group(context):
    context['message'] = re.sub(' +', ' ', context['message']).strip()

    if await preHandle(context):
        return ''

    for start in startswith_group:
        if context['message'].strip().startswith(start):
            reply = await startswith_group[start](context)
            return reply
    for end in endswith_group:
        if context['message'].strip().endswith(end):
            reply =  await endswith_group[end](context)
            return reply
    # reply = await customQA(context)
    # return reply
    return ''



startswith_private = {
    '续费': addTime,
    '设置宏': setHongAdmin,
    '退群': exitGroup,
}

async def parse_private(context):
    if context['user_id'] != 986859110:
        if 'CQ:rich' in context['message']:
            return ''
        return "你好! 我是QQ小橙, 是个团队排表机器人!\n如果要引入或者续费 请加QQ群716860454"
    context['message'] = re.sub(' +', ' ', context['message']).strip()
    for start in startswith_private:
        if context['message'].startswith(start):
            return await startswith_private[start](context)
    return context['message']

async def handle_request(context):
    return await handle_invite(context)