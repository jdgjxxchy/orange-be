#!/usr/bin/env python
# encoding: utf-8

from models import User, Group, Team, Template, Hong, Gold
from utils.common import getString
from utils.get_gold import get_gold
from views.data import getTeamDetail, getTemplates, getTemplateDetail, getUserDetail
from config import BASE_DIR
import datetime


import json

async def sendData(group, bot, msg):
    await bot.redis.publish(f'channel:{group}', msg)

async def login(username, password, groupNumber):
    group = Group().getByGroup(groupNumber)
    if not group:
        return json.dumps({"res": "fail", "msg": "该群无权限, 请先购买小橙"})
    user = User().getByQG(username, group)
    if not user:
        return json.dumps({"res": "fail", "msg": "该群内QQ不存在, 请先至少在群内发言一次"})
    if user.password.strip() != password:
        return json.dumps({"res": "fail", "msg": "密码错误"})
    token = getString(25)
    user.token = token
    user.save()
    return json.dumps({"res":"success", "token": token})

def createTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有增加团队的权限, 请联系群管理员修改权限'})
    teams = Team().getByGroup(user.group)
    if len(teams) >= user.group.maxTeam:
        return json.dumps({'req': 'error', 'data': '团队数量已达上限, 请联系小橙作者增加上限'})
    team = Team(qq=user.qq, name=data['name'], startTime=data['startTime'], tip=data['tip'], sign=data['sign'],group=user.group)
    team.add()
    return getTeamDetail(team, 'createTeam')

def putTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作团队的权限, 请联系群管理员修改权限'})
    team = Team().getById(data['id'])
    if not team: return json.dumps({'req': 'error', 'data':'请刷新页面重试'})
    for key in data:
        setattr(team, key, data[key])
    team.save()
    return getTeamDetail(team)

def delTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有删除团队的权限, 请联系群管理员修改权限'})
    team = Team().getById(data['id'])
    team.delete_at = datetime.datetime.now()
    team.save()
    return json.dumps({'req': 'delTeam', 'data': {'id': data['id']}})


def putUser(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作团员的权限, 请联系群管理员修改权限'})
    cUser = User().getById(data['id'])
    for key in data:
        setattr(cUser, key, data[key])
    cUser.save()
    return getUserDetail(cUser, 'putUser')

def delUser(user, data):
    auth = user.auth[0]
    print(user.id, user.auth[0])
    users = []
    for id in data:
        u = User().getById(id)
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
        u.delete()
    return json.dumps({'req': 'delUser', 'data': data})

def createTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有增加模板的权限, 请联系群管理员修改权限'})
    templates = Template().getByGroup(user.group)
    if len(templates) >= user.group.maxTemplate:
        return json.dumps({'req': 'error', 'data': '团队模板数量已达上限, 请联系小橙作者增加上限'})
    template = Template(qq=user.qq, name=data['name'], group=user.group)
    if 'members' in data: template.members = data['members']
    template.add()
    return getTemplateDetail(template, 'createTemplate')

def putTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有操作模板的权限, 请联系群管理员修改权限'})
    template = Template().getById(data['id'])
    for key in data:
        setattr(template, key, data[key])
    template.save()
    return getTemplateDetail(template)

def delTemplate(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有删除模板的权限, 请联系群管理员修改权限'})
    Template().deleteById(data['id'])
    return json.dumps({'req': 'delTemplate', 'data': {'id': data['id']}})

def getTemplateList(user, data):

    return getTemplates(user)

def putPwd(user, data):
    if data['oldPwd'] != user.password:
        return json.dumps({'req': 'error', 'data':'当前密码填写错误'})
    user.password = data['newPwd']
    user.save()
    return json.dumps({'req': 'putPwd', 'data': '密码修改成功'})

def putHong(user, data):
    if user.auth[0] == '0':
        return json.dumps({'req': 'error', 'data':'非管理员请在群内使用设置宏口令修改'})
    Hong().setHong(user.qq, user.group.group, data['occu'], data['content'])
    return json.dumps({'req': 'putPwd', 'data': f'{data["occu"]}宏修改成功'})

def syncHong(user, data):
    if user.auth[0] == '0':
        return json.dumps({'req': 'error', 'data':'非管理员无法设置同步宏'})
    print(data)
    hong = Hong().getByGroup(user.group.group, data['occu'])
    print(hong, user.group.group)
    if hong:
        hong.delete()
        return json.dumps({'req': 'syncHong', 'data': f'{data["occu"]}宏已恢复同步, 请点左上角刷新按钮刷新数据'})

async def putGold(user, data, bot):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data':'你谁?调用这个接口?'})
    gold = Gold().getGoldByArea(data['area'])
    if gold is None:
        Gold(**data).add()
    else:
        for key in data:
            setattr(gold, key, data[key])
        gold.save()
    await get_gold(bot.req, data['area'])
    return json.dumps({'req': 'putGold', 'data': ''})

def putGroup (user, data):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data':'你谁?调用这个接口?'})
    group = Group().getByGroup(data['oldGroup'])
    del data['oldGroup']
    for key in data:
        setattr(group, key, data[key])
    group.save()
    return json.dumps({'req': 'putGroup', 'data': ''})

def getDelTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有查看删除团队的权限, 请联系群管理员修改权限'})
    teams = Team().getDel(user.group)
    res = {'req': 'getDelTeam', 'data': []}
    for team in teams:
        res['data'].append({
            "id": team.id,
            "name": team.name,
            "startTime": team.startTime,
            "delete_at": team.delete_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return json.dumps(res)

def recoverDelTeam(user, data):
    if user.auth[1] != '1':
        return json.dumps({'req': 'error', 'data':'您没有恢复团队的权限, 请联系群管理员修改权限'})
    recover = user.group.recover_at
    now = datetime.date.today()
    if recover and (now - recover).days < 7 and now.weekday() >= recover.weekday():
        return json.dumps({'req': 'error', 'data':'一周内只能恢复一次团队'})
    user.group.recover_at = now
    Team().recover(data['id'])
    return json.dumps({'req': 'recoverDelTeam', 'data': '团队恢复成功'})

async def getMoney(user, data, bot):
    if user.qq != '986859110':
        return json.dumps({'req': 'error', 'data': '你谁?调用这个接口?'})
    index = 0
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
        await bot.send_group_msg(self_id=i['robot'], group_id=i['group'], message=text)
    return json.dumps({'req': 'putHong', 'data': '催费成功'})