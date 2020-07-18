#!/usr/bin/env python
# encoding: utf-8

from models import User, Group, Team, Template, Hong, Gold
from utils.common import getString
from utils.get_gold import get_gold
from views.data import getTeamDetail, getTemplates, getTemplateDetail, getUserDetail
from config import BASE_DIR
from tortoise.query_utils import Q
from quart import jsonify
import datetime


import json

async def sendData(group, bot, msg):
    await bot.redis.publish(f'channel:{group}', msg)

async def login(username, password, groupNumber):
    group = await Group.get_or_none(group=groupNumber)
    if not group:
        return json.dumps({"res": "fail", "msg": "该群无权限, 请先购买小橙"})
    user = await User.get_or_none(qq=username, group=group)
    if not user:
        return json.dumps({"res": "fail", "msg": "该群内QQ不存在, 请先至少在群内发言一次"})
    if user.password.strip() != password:
        return json.dumps({"res": "fail", "msg": "密码错误"})
    token = getString(25)
    user.token = token
    await user.save()
    return jsonify({"res":"success", "token": token})

async def createTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有增加团队的权限, 请联系群管理员修改权限'})
    group = await user.group
    teams = await Team.filter(group=group, delete_at=None).all()
    if len(teams) >= group.maxTeam:
        return json.dumps({'req': 'error', 'data': '团队数量已达上限, 请联系小橙作者增加上限'})
    team = await Team.create(qq=user.qq, name=data['name'], startTime=data['startTime'], tip=data['tip'], sign=data['sign'],group=group)
    return getTeamDetail(team, 'createTeam')

async def putTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作团队的权限, 请联系群管理员修改权限'})
    team = await Team.get_or_none(id=data['id'])
    if not team: return json.dumps({'req': 'error', 'data':'请刷新页面重试'})
    for key in data:
        setattr(team, key, data[key])
    await team.save()
    return getTeamDetail(team)

async def delTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有删除团队的权限, 请联系群管理员修改权限'})
    team = await Team.get_or_none(id=data['id'])
    team.delete_at = datetime.datetime.now()
    await team.save()
    return json.dumps({'req': 'delTeam', 'data': {'id': data['id']}})


async def putUser(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作团员的权限, 请联系群管理员修改权限'})
    cUser = await User.get_or_none(id=data['id'])
    for key in data:
        setattr(cUser, key, data[key])
    await cUser.save()
    return getUserDetail(cUser, 'putUser')

async def delUser(user, data):
    auth = user.auth[0]
    users = []
    for id in data:
        u = await User.get_or_none(id=id)
        if auth == '2': users.append(u)
        if auth == '1':
            if u.auth[0] == '2' or (u.auth[0] == '1' and id != user.id):
                return json.dumps({'req': 'error', 'data':'您没有删除团员的权限'})
            users.append(u)
        if auth == '0':
            if id != user.id:
                return json.dumps({'req': 'error', 'data': '您没有删除团员的权限'})
            users.append(u)
    for u in users:
        await u.delete()
    return json.dumps({'req': 'delUser', 'data': data})

async def createTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有增加模板的权限, 请联系群管理员修改权限'})
    group = await user.group
    templates = await Template.filter(group=group).all()
    if len(templates) >= group.maxTemplate:
        return json.dumps({'req': 'error', 'data': '团队模板数量已达上限, 请联系小橙作者增加上限'})
    template = await Template.create(qq=user.qq, name=data['name'], group=group)
    if 'members' in data: template.members = data['members']
    await template.save()
    return getTemplateDetail(template, 'createTemplate')

async def putTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作模板的权限, 请联系群管理员修改权限'})
    template = await Template.get_or_none(id=data['id'])
    for key in data:
        setattr(template, key, data[key])
    await template.save()
    return getTemplateDetail(template)

async def delTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有删除模板的权限, 请联系群管理员修改权限'})
    temp = await Template.get_or_none(id=data['id'])
    if temp:
        await temp.delete()
        return json.dumps({'req': 'delTemplate', 'data': {'id': data['id']}})


async def putPwd(user, data):
    if data['oldPwd'] != user.password:
        return json.dumps({'req': 'error', 'data':'当前密码填写错误'})
    user.password = data['newPwd']
    await user.save()
    return json.dumps({'req': 'putPwd', 'data': '密码修改成功'})

async def putHong(user, data):
    if user.auth[0] == '0':
        return json.dumps({'req': 'error', 'data':'非管理员请在群内使用设置宏口令修改'})
    group = await user.group
    await Hong.setHong(user.qq, group.group, data['occu'], data['content'])
    return json.dumps({'req': 'putPwd', 'data': f'{data["occu"]}宏修改成功'})

async def syncHong(user, data):
    if user.auth[0] == '0':
        return json.dumps({'req': 'error', 'data':'非管理员无法设置同步宏'})
    group = await user.group
    hong = await Hong.get_or_none(group=group.group, occu=data['occu'])
    if hong:
        await hong.delete()
        return json.dumps({'req': 'syncHong', 'data': f'{data["occu"]}宏已恢复同步, 请点左上角刷新按钮刷新数据'})

async def putGold(user, data, bot):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data':'你谁?调用这个接口?'})
    gold, _ = await Gold.get_or_create(data, area=data['area'])
    for key in data:
        setattr(gold, key, data[key])
    await gold.save()
    await get_gold(bot.req, data['area'])
    return json.dumps({'req': 'putGold', 'data': ''})

async def putGroup (user, data):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data':'你谁?调用这个接口?'})
    group = await Group.get_or_none(group=data['oldGroup'])
    del data['oldGroup']
    for key in data:
        setattr(group, key, data[key])
    await group.save()
    return json.dumps({'req': 'putGroup', 'data': ''})

async def getTemplateList(user, data):

    return await getTemplates(user)

async def getDelTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有查看删除团队的权限, 请联系群管理员修改权限'})
    group = await user.group
    teams = await Team.filter(Q(group=group), ~Q(delete_at=None)).order_by('-delete_at').limit(3).all()
    res = {'req': 'getDelTeam', 'data': []}
    for team in teams:
        res['data'].append({
            "id": team.id,
            "name": team.name,
            "startTime": team.startTime,
            "delete_at": team.delete_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return json.dumps(res)

async def recoverDelTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有恢复团队的权限, 请联系群管理员修改权限'})
    group = await user.group
    recover = group.recover_at
    now = datetime.date.today()
    if recover and (now - recover).days < 7 and now.weekday() >= recover.weekday():
        return json.dumps({'req': 'error', 'data':'一周内只能恢复一次团队'})
    group.recover_at = now
    await group.save()
    await Team.filter(id=data['id']).update(delete_at=None)
    return json.dumps({'req': 'recoverDelTeam', 'data': '团队恢复成功'})

async def getMoney(user, data, bot):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data': '你谁?调用这个接口?'})
    index = 0
    err = []
    for i in data:
        days = i['days']
        index += 1
        s = f'[CQ:image,file=file:///{BASE_DIR}\image\cuifei.png]'
        if days > 0:
            text = f'{s}\n小橙还有{days}天就要到时间拉'
        elif days == 0:
            text = f'{s}\n小橙今天结束就要到时间拉'
        else:
            text = f'{s}\n小橙已经过期{-days}天拉'
        try:
            await bot.send_group_msg(self_id=i['robot'], group_id=i['group'], message=text)
        except:
            err.append(str(i['group']))
    return json.dumps({'req': 'putHong', 'data': f'催费成功{str(index)}个群, {" ".join(err)}失败'})