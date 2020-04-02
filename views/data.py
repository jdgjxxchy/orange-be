#!/usr/bin/env python
# encoding: utf-8


from models import Team, User, Template, Hong, Gold, Group
from utils.dicts import occuList
from quart import jsonify
import datetime
from main import db

import json

def getUser(token):
    return User().getByToken(token)

def getGoldList(user):
    if user.qq != '986859110':
        return jsonify({})
    golds = Gold().query.all()
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

def getDays(info):
    today = datetime.date.today()
    for groupDic in info:
        group = Group().getByGroup(groupDic['group_id'])
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
    for robot in bot._connected_ws_reverse_api_clients:
        info = await bot.get_group_list(self_id=int(robot))
        res = getDays(info)
        s["list"].append({
            "robot": int(robot),
            "res": res
        })
    return jsonify(s)

async def getMoney(user, bot):
    if user.qq != '986859110':
        return jsonify({})

def getGroupList(user):
    if user.qq != '986859110':
        return jsonify({})
    groups = Group().query.all()
    now = datetime.date.today()
    res = []
    for group in groups:
        if group.expire >= now:
            res.append({
                "id": group.id,
                "group": group.group,
                "expire": group.expire,
                "days": (group.expire - now).days,
                "robot": group.robot,
                "maxTeam": group.maxTeam,
                "maxTemplate": group.maxTemplate,
                "maxQA": group.maxQA,
            })
    return jsonify(res)


def getTeamList(user):
    teams = Team().getByGroup(user.group)
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

def getUserList(user):
    users = User().getByGroup(user.group)
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

def getHongList(user):
    res = []
    for occu in occuList:
        hong = Hong().getByOccu(occu, user.group.group)
        if len(hong) > 0:
            content = hong[0].content
        else:
            content = ''
        res.append({
            "occu": occu,
            "content": content
        })
    return jsonify(res)

def getTemplates(user):
    res = {'req': 'getTemplateList'}
    temps = Template().getByGroup(user.group)
    res["data"] = []
    for temp in temps:
        res["data"].append({
            "id": temp.id,
            "qq": temp.qq,
            "name": temp.name,
            "members": temp.members,
        })
    return json.dumps(res, ensure_ascii=False)

def getUserInfo(user):
    group = user.group
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
        "expire": group.expire,
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

