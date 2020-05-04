#!/usr/bin/env python
# encoding: utf-8


from views.data import *
from views.handlers import *
import json


async def handleData(user, bot, data):
    if user is None:
        return json.dumps({'req': 'error', 'data':'token已过期,请重新登录'})
    gl= await user.group
    group = gl.group
    data = json.loads(data)
    operate = {
        'createTeam': createTeam,
        'putTeam': putTeam,
        'delTeam': delTeam,
        'putUser': putUser,
        'delUser': delUser,
        'createTemplate': createTemplate,
        'putTemplate': putTemplate,
        'delTemplate': delTemplate,
        'getTemplateList': getTemplateList,
        'putPwd': putPwd,
        'putHong': putHong,
        'syncHong': syncHong,
        'putGroup': putGroup,
        'getDelTeam': getDelTeam,
        'recoverDelTeam': recoverDelTeam,
    }
    if data['req'] == 'putGold':
        res = await putGold(user, data['data'], bot)
    elif data['req'] == 'getMoney':
        res = await getMoney(user, data['data'], bot)
    else:
        res = await operate[data['req']](user, data['data'])
    await sendData(group, bot, res)


async def handle_http(command, bot, token):
    operate = {
        'teamList': getTeamList,
        'userList': getUserList,
        'userInfo': getUserInfo,
        'hongList': getHongList,
        'goldList': getGoldList,
        'groupList': getGroupList,
    }
    user = await getUser(token)
    if not user:
        return json.dumps({"res":"fail", "msg": "登录已过期"})
    if command == 'robotInfo':
        res = await getRobotInfo(user, bot)
    else:
        res = await operate[command](user)
    return res