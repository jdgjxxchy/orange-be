#!/usr/bin/env python
# encoding: utf-8


from models import Team, User, Template, Hong, Gold, Group
from tortoise.query_utils import Q
from utils.dicts import occuList
from quart import jsonify
import datetime

import json

async def getUser(token):
    return await User.get_or_none(token=token)

async def getGoldList(user):
    if user.qq != '986859110':
        return jsonify({})
    golds = await Gold.all()
    res = []
    for gold in golds:
        res.append({
            "area": gold.area,
            "url5173": gold.url5173,
            "urlOfficial": gold.urlOfficial,
            "urlPost": gold.urlPost,
            "gold": gold.gold,
        })
    return jsonify(res)

async def getDays(info):
    today = datetime.date.today()
    for groupDic in info:
        group = await Group.get_or_none(group=groupDic['group_id'])
        del groupDic['member_count']
        del groupDic['max_member_count']
        if group:
            days = (group.expire - today).days
            groupDic['days'] = days
        else:
            groupDic['days'] = -1000
    return sorted(info, key=lambda dic: dic['days'], reverse=False)

async def getRobotInfo(user, bot):
    if user.qq != '986859110':
        return jsonify({})
    s = {
        # "robots": list(bot._connected_ws_reverse_api_clients.keys()),
        "robots": json.load(open('src/robots.json', 'r')),
        "list": [],
    }
    for robot in bot._wsr_api_clients:
        info = await bot.get_group_list(self_id=int(robot))
        res = await getDays(info)
        s["list"].append({
            "robot": int(robot),
            "res": res
        })
    return jsonify(s)


async def getGroupList(user):
    if user.qq != '986859110':
        return jsonify({})
    groups = await Group.all()
    now = datetime.date.today()
    res = []
    for group in groups:
        if group.expire >= now:
            res.append({
                "id": group.id,
                "group": group.group,
                "expire": str(group.expire),
                "days": (group.expire - now).days,
                "robot": group.robot,
                "maxTeam": group.maxTeam,
                "maxTemplate": group.maxTemplate,
                "maxQA": group.maxQA,
            })
    return jsonify(res)


async def getTeamList(user):
    group = await user.group
    teams = await Team.filter(group=group, delete_at=None).all()
    res = []
    for team in teams:
        res.append({
            "id": team.id,
            "startTime": team.startTime,
            "name": team.name,
            "members": json.loads(team.members),
            "alternate": json.loads(team.alternate),
            "tip": team.tip,
            "sign": team.sign,
            "qq": team.qq,
            "created_at": team.create_at.strftime('%Y-%m-%d %H:%M:%S'),
            "update_at": team.update_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return jsonify(res)

async def getUserList(user):
    group = await user.group
    users = await User.filter(group=group).all()
    res = []
    for user in users:
        res.append({
            "id": user.id,
            "qq": user.qq,
            "name": user.name,
            "auth": user.auth,
            "tip": user.tip,
            "absent": user.absent,
        })
    return jsonify(res)

async def getHongList(user):
    res = []
    group = await user.group
    for occu in occuList:
        hong = await Hong.filter(Q(occu=occu), Q(group=group.group) | Q(group='0')).order_by('group').all()
        if len(hong) > 0:
            content = hong[0].content
        else:
            content = ''
        res.append({
            "occu": occu,
            "content": content
        })
    return jsonify(res)

async def getTemplates(user):
    res = {'req': 'getTemplateList'}
    group = await user.group
    temps = await Template.filter(group=group).all()
    res["data"] = []
    for temp in temps:
        res["data"].append({
            "id": temp.id,
            "qq": temp.qq,
            "name": temp.name,
            "members": temp.members,
        })
    return json.dumps(res, ensure_ascii=False)

async def getUserInfo(user):
    group = await user.group
    res = {
        "user_id": user.id,
        "qq": user.qq,
        "user_name": user.name,
        "auth": user.auth,
        "group": group.group,
        "group_name": group.name,
        "robot": group.robot,
        # "owner": group.owner == user.id,
        "maxTeam": group.maxTeam,
        "maxTemplate": group.maxTemplate,
        "maxQA": group.maxQA,
        "expire": str(group.expire),
    }
    return jsonify(res)

def getTeamDetail(team, req='putTeam'):
    res = {'req': req}
    res['data'] = {
        'id': team.id,
        'qq': team.qq,
        'startTime': team.startTime,
        'name': team.name,
        'members': json.loads(team.members),
        'alternate': json.loads(team.alternate),
        "tip": team.tip,
        "sign": team.sign,
        "created_at": team.create_at.strftime('%Y-%m-%d %H:%M:%S'),
        "update_at": team.update_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    return json.dumps(res, ensure_ascii=False)

def getTemplateDetail(temp, req='putTemplate'):
    res = {'req': req}
    res['data'] = {
        'id': temp.id,
        'qq': temp.qq,
        'name': temp.name,
        'members': temp.members,
    }
    return json.dumps(res, ensure_ascii=False)

def getUserDetail(user, req):
    res = {'req': req}
    res['data'] = {
        "id": user.id,
        "qq": user.qq,
        "name": user.name,
        "auth": user.auth,
        "tip": user.tip,
        "absent": user.absent,
    }
    return json.dumps(res, ensure_ascii=False)

