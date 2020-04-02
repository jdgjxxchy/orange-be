#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: team.py
@time: 2020/1/17

"""

from models import Team, Template, User
from utils.dicts import teamType, signOrder, occuDic, occuList
from utils.common import gap, find_in_dic
from utils.draw import drawTeam
from views.handlers import sendData
from views.data import getTeamDetail, getUserDetail
from main import db
import datetime
import json
import asyncio
import functools

# 开团
async def startTeam(context):
    group = context['info']['group']
    teams = Team().getByGroup(group)
    if context['message'] == '开团':
        return  \
            '开团指令为:"开团 副本类型 时间"\n' \
            '[副本类型]为("挑战jmw", "挑战ttd", "普通敖龙岛", "英雄敖龙岛"),必填\n' \
            '[时间]为("今天X点","a月b日X点") 等只要你能看得懂的(建议填完整时间 必填)\n' \
            '例如:[开团 英雄敖龙岛 今天七点][开团 英雄hxl 今天八点半 1]\n'
    a = context['message'].replace('开团', '').strip().split(' ')
    user = context['info']['user']
    if len(a[0]) > 6 : return ''
    if user.auth[1] != '1': return '没有权限开团, 只有管理员和设定了权限的人才可以开团'
    if len(a) < 2: return '开团请写清楚 副本类型 和 开团时间哦'
    if a[0] not in teamType: return '请输入正确的副本团队. 回复"开团"获取帮助'
    if len(teams) >= group.maxTeam: return '抱歉,我们群开的团到达上限 请先取消已经开的团或者联系QQ986859110增加开团上限'
    text = f'开团成功! {group.name} 团的 {a[0]} 将于 {a[1]} 准时出发!取消开团请回复 取消开团 团队编号'
    template = None
    if len(a) > 2:
        templateId = a[2]
        if not templateId.isdigit(): return '请输入正确的模板号. 回复"模板"获取帮助'
        templates = Template().getByGroup(group)
        tId = int(templateId)
        if tId > len(templates): return f"没有编号为{tId}的模板"
        template = templates[int(templateId) - 1].members
        text += f'\n模板{tId}使用成功'
    team = Team(qq=user.qq, name=a[0], startTime=a[1], group=group)
    if template: team.members = template
    team.add()
    await sendData(group.group, context['info']['bot'], getTeamDetail(team, 'createTeam'))
    return text

# 取消开团
async def cancelTeam(context):
    group = context['info']['group']
    user = context['info']['user']
    if user.auth[1] != '1': return '你没有权限取消开团'
    teams = Team().getByGroup(group)
    if not teams: return '目前没有准备开的团!'
    if context['message'] in ['取消开团', '取消团队', '删除团队']:
        text = '本群有以下团:\n'
        for index, team in enumerate(teams, start=1):
            text += f'{index}. 于{team.startTime}开的{team.name}\n'
        text += '取消开团回复 取消开团 团队编号  '
        return text
    a = context['message'].replace('取消', '').replace('删除', '').replace('开团', '').replace('团队', '').strip()
    if not a.isdigit(): return "命令有误, 回复 取消开团 查看具体指令"
    n = int(a) - 1
    if n >= len(teams) or n < 0: return f'没有编号为{a}的团'
    teams[n].delete_at = datetime.datetime.now()
    teams[n].save()
    text = f'于{teams[n].startTime}开的{teams[n].name}取消成功'
    await sendData(group.group, context['info']['bot'], json.dumps({'req': 'delTeam', 'data': {'id': teams[n].id}}))
    return text

# 查看团队
async def getTeam(context):
    group = context['info']['group']
    teams = Team().getByGroup(group)
    if context['message'] in ['查看团队']:
        if not teams: return '目前没有人在开团, 请联系管理员开团'
        text = '本群有以下团\n'
        for index, team in enumerate(teams, start=1):
            text += f'{index}. 于{team.startTime}开的{team.name},权限:{team.sign}\n'
        url = 'http://orange.arkwish.com'
        text += '[查看团队 团队编号] 查看具体信息\n' \
                '网页查看和编辑复制到浏览器:  ' + url
        return text
    a = context['message'].replace('查看团队', '').strip().split(' ')
    if len(a) != 1 or not a[0].isdigit(): return '请输入正确的团队编号 例如[查看团队 1]'
    n = int(a[0])
    if n > len(teams) or n < 1: return f'没有编号为{n}的团'
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(drawTeam, teams[n - 1], group))


def nobody(member):
    return 'player' not in member and 'client' not in member

# 报名
async def signUp(context):

    if context['message'] in ['报名', '我要报名']:
        return "报名格式: 我要报名 职业 团队编号\n团队编号请回复 查看团队 获取\n职业和团队编号之间要有空格,团队编号不填默认为1"
    user = context['info']['user']
    group = context['info']['group']
    teams = Team().getByGroup(group)
    isD = '代' in context['message']
    a = context['message'].replace('报名', '').replace('我要', '').replace('代','').strip().split(' ')
    occu, occuOrigin = find_in_dic(context['message'], occuDic)
    if not occu or (a[0].replace(occuOrigin, '').replace('双修','').replace('双休','') != ''):
        return '报名命令:[我要报名 职业 团队序号]空格隔开 如果没有序号默认报名1号团队\n职业名请填写剑网三职业'
    occuIndex = occuList.index(occu)
    teamNum = 0
    if len(a) > 1:
        if a[1].isdigit(): teamNum = int(a[1]) - 1
        else: return "团队编号必须为数字 例如 报名 花间 2"
    if teamNum > len(teams) - 1 or teamNum < 0: return f'没有编号为{teamNum+1}的团'
    team = teams[teamNum]
    if int(user.auth[2]) < team.sign: return '您不可以在该团队报名或者代开, 请联系团长调整您的权限'
    team = teams[teamNum]
    members = json.loads(team.members)
    for i in members:
        if not isD and 'player' in i and 'id' in i['player'] and i['player']['id'] == user.id:
            return '您已报名该团,请不要重复报名\n若要修改职业请先取消报名后再重新报名'
    position = -1
    isDouble = '双' in context['message']
    # 报名双修 优先搜索带有双修要求的坑
    if position == -1 and isDouble:
        for index, i in enumerate(members):
            if nobody(i) and 'onlyClient' not in i and 'mustDouble' in i and 'occuList' in i and occuIndex in i['occuList']:
                position = index
                break

    # 其次搜索带有occuList字段的坑
    if position == -1:
        for index, i in enumerate(members):
            if nobody(i) and 'onlyClient' not in i and 'occuList' in i and occuIndex in i['occuList']:
                if 'mustDouble' in i and i['mustDouble']:
                    if isDouble:
                        position = index
                        break
                    else: continue
                position = index
                break

    # 最后搜索空白字段
    if position == -1:
        for i in signOrder[occu]:
            if nobody(members[i])  and 'onlyClient' not in members[i] and 'occuList' not in members[i]:
                position = i
                break
    if position == -1:
        alt = json.loads(team.alternate)
        alt.append({
            "id": user.id,
            "occu": occuIndex,
        })
        team.alternate = json.dumps(alt, ensure_ascii=False)
        team.save()
        await sendData(group.group, context['info']['bot'], getTeamDetail(team))
        return '没有报名的位置拉, 已将您报名的该职业加入替补列表, 团长安排的时候会在网页的替补名单看到您.'
    members[position]['player'] = { "id" :user.id }
    members[position]['occu'] = occuIndex
    if isDouble: members[position]['double'] = True
    team.members = json.dumps(members, ensure_ascii=False)
    team.save()
    await sendData(group.group, context['info']['bot'], getTeamDetail(team))
    return f'{user.name}成功报名于{team.startTime}发车的{team.name}\n查看团队情况 请回复"查看团队 {teamNum+1}" 取消报名请回复"取消报名 {teamNum+1}" '

# 取消报名
async def cancelSignUp(context):
    if context['message'] in ['取消报名']:
        return '取消报名命令: 取消报名 团队编号 职业\n' \
               '团队编号请回复 查看团队 获取 如果一个团只报名了一种职业,则可以不填.'
    user = context['info']['user']
    group = context['info']['group']
    teams = Team().getByGroup(group)
    occu, occuPre = find_in_dic(context['message'], occuDic)
    a = context['message'].replace('取消报名', '').strip()
    if occu: a = a.replace(occuPre, '').strip()
    if a.isdigit():
        n = int(a)
        if n > len(teams) or n < 1:
            return '没有编号为{}的团'.format(n)
        team = teams[n - 1]
        members = json.loads(team.members)
        for index, i in enumerate(members):
            if 'player' in i and 'id' in i['player'] and i['player']['id'] == user.id:
                if occu and 'occu' in i and occuList[i['occu']] != occu:
                    continue
                signOccu = occuList[i['occu']] if 'occu' in i else '无职业'
                if 'client' not in i and 'occu' in i:
                    del i['occu']
                del i['player']
                if 'double' in i: del i['double']
                team.members = json.dumps(members, ensure_ascii=False)
                team.save()
                await sendData(group.group, context['info']['bot'], getTeamDetail(team))
                return f'{user.name}在{team.startTime}开的{team.name}报名的{signOccu}已取消报名成功'
        return f'您并没有报名于{team.startTime}开的{team.name}'
    return '取消报名命令: 取消报名 团队编号 职业\n' \
               '团队编号请回复 查看团队 获取 如果一个团只报名了一种职业,则可以不填.'

# 登记老板
async def recordClient(context):
    if context['message'] in ['登记老板']:
        text = '登记老板 职业 团队编号 老板备注\n' \
               '团队不填默认为1, 老板备注尽量精简短小\n' \
               '例如[登记老板 焚影][登记老板 焚影 2][登记老板 焚影 1 3W包][登记老板 焚影 1 3W包,装分39000]'
        return text
    user = context['info']['user']
    group = context['info']['group']
    if user.auth[3] != '1': return '您没有权限登记老板'
    teams = Team().getByGroup(group)
    occu, preOccu = find_in_dic(context['message'], occuDic)
    if not occu: return '老板的职业和团队编号之间要记得空格, 老板职业必须为剑网三职业'
    occuIndex = occuList.index(occu)
    a = context['message'].replace('登记老板', '').replace(preOccu, '').strip().split(' ')
    teamNum = 0
    if a[0].isdigit(): teamNum = int(a[0]) - 1
    if teamNum > len(teams) - 1 or teamNum < 0:
        return '没有编号为{}的团'.format(teamNum + 1)
    if a[0].isdigit():
        tip = ' '.join(a[1:]) if len(a) > 1 else ''
    else:
        tip = ' '.join(a[0:])
    team = teams[teamNum]
    members = json.loads(team.members)
    position = -1
    # 优先搜索空白坑
    if position == -1:
        for index, i in enumerate(members):
            if nobody(i) and 'occuList' not in i:
                position = index
                break

    if position == -1:
        for index, i in enumerate(members):
            if nobody(i) and 'canClient' in i and 'occuList' in i and occuIndex in i['occuList']:
                position = index
                break

    if position == -1:
        return f'没有老板的位置拉,请取消老板或修改团队后再登记.\n具体团队情况请回复 查看团队 {teamNum + 1} 进行查看'
    members[position]['client'] = { 'whose': user.id, 'tip': tip}
    members[position]['occu'] = occuIndex
    team.members = json.dumps(members, ensure_ascii=False)
    team.save()
    await sendData(group.group, context['info']['bot'], getTeamDetail(team))
    return f'老板登记成功!{user.name}喊的 {occu} 老板已登记到于{team.startTime}发车的{team.name}团队\n输入"查看团队 {teamNum+1}"即可查看'

def getClientsFromTeam(teams, user):
    clients = []
    for index, team in enumerate(teams):
        members = json.loads(team.members)
        for tIndex, mem in enumerate(members):
            if 'client' in mem and 'occu' in mem and 'whose' in mem['client'] and mem['client']['whose'] == user.id:
                clients.append([index + 1, occuList[mem['occu']], tIndex, mem['client']])
    return clients

# 取消老板
async def cancelClient(context):
    user = context['info']['user']
    group = context['info']['group']
    if user.auth[3] != '1': return '您没有权限取消老板'
    teams = Team().getByGroup(group)
    clients = getClientsFromTeam(teams, user)
    if context['message'] in ['取消老板','删除老板']:
        text = "你目前喊到的老板如下:\n"
        for i, client in enumerate(clients):
            text += f"{i + 1}. 团队号:{client[0]} 职业:{client[1]}\n"
        return text+ "取消老板的格式为 '取消老板 老板序号', 一经取消不可恢复, 请慎重取消"
    a = context['message'].replace('取消老板', '').strip()
    if not (a.isdigit() and int(a)<=len(clients) and int(a)>0):
        return "请输入正确格式 取消老板 老板序号. 获得编号请回复 取消老板"
    c = clients[int(a) - 1]
    print(c)
    members = json.loads(teams[c[0] - 1].members)
    del members[c[2]]['client']
    if 'player' not in members[c[2]]: del members[c[2]]['occu']
    teams[c[0] - 1].members = json.dumps(members, ensure_ascii=False)
    teams[c[0] - 1].save()
    await sendData(group.group, context['info']['bot'], getTeamDetail(teams[c[0] - 1]))
    return f'老板取消成功!{user.name}在团队 {c[0]} 喊的 {c[1]} 老板已取消\n输入"查看团队 {c[0]}"即可查看'

async def getClients(context):
    user = context['info']['user']
    group = context['info']['group']
    teams = Team().getByGroup(group)
    clients = getClientsFromTeam(teams, user)
    if context['message'] in ['查看老板']:
        text = "你目前喊到的老板如下:\n"
        for i, client in enumerate(clients):
            text += f"{i + 1}. 团队号:{client[0]} 职业:{client[1]}\n"
            if 'tip' in client[3] and client[3]['tip'] != '':
                text += f"备注: {client[3]['tip']}\n"
        return text + "需要取消老板 回复 取消老板 老板号"


# 改名
@gap('editName', 5)
async def editName(context):
    if context['message'] in ['修改昵称', '改名']:
        return '改名的命令为:  改名 新昵称\n管理员可以用[改名 新昵称 QQ号]修改任意用户'
    a = context['message'].strip().split(' ')
    if not (a[0] == '修改昵称' or  a[0] == '改名') or len(a) < 2:
        return ''
    user = context['info']['user']
    group = context['info']['group']
    try:
        if len(a) == 2:
            user.changeName(a[1])
            await sendData(group.group, context['info']['bot'], getUserDetail(user, 'putUser'))
            return f'{user.qq}成功修改昵称为{a[1]},修改昵称群内CD5秒 建议去网页修改'
        if len(a) == 3 and a[2].isdigit():
            if user.auth[0] == '0': return '对不起,您没有权限修改他人昵称'
            User().changeOtherName(a[2], group, a[1])
            return '成功将{}的昵称修改为{}'.format(a[2], a[1])
    except:
        db.session.rollback()
        return '输入有误,无法修改昵称'

# 修改团名
async def editTeamName(context):
    if context['message'] in ['修改团名']:
        return '指令: 修改团名 新团队名称'
    group = context['info']['group']
    user = context['info']['user']
    if user.auth[1] == '0': return '对不起,您没有权限修改团名'
    name = context['message'].replace('修改团名','').strip()
    try:
        group.changeName(name)
    except:
        db.session.rollback()
        return "团队名称含有非法字符."
    return '团队修改成功!团名为%s' % name

# 设置团队备注
async def setTip(context):
    group = context['info']['group']
    user = context['info']['user']
    if user.auth[1] == '0': return '对不起,您没有权限修改团队备注'
    text = "设置团队备注 团队编号 备注内容\n" \
            "可以写上小铁瑰石归属,报名方法,团长真帅等备注.通过 查看团队 团队编号可以看到"
    if context['message'] in ['设置团队备注']: return text
    a = context['message'].replace('设置团队备注', '').strip().split(' ')
    if not (len(a)== 2 and a[0].isdigit()): return text
    teams = Team().getByGroup(group)
    teamNum = int(a[0])
    if teamNum > len(teams) or teamNum < 1: return f"没有编号为{teamNum}的团"
    teams[teamNum-1].setTip(a[1])
    await sendData(group.group, context['info']['bot'], getTeamDetail(teams[teamNum-1]))
    return f"团队备注修改成功! 回复 查看团队 {teamNum} 即可查看"

# 设置报名权限
async def setSignAuth(context):
    group = context['info']['group']
    user = context['info']['user']
    if user.auth[1] == '0': return '对不起,您没有权限修改团队报名权限'
    text = "设置报名权限 团队编号 权限编号\n" \
           "群成员默认权限为1, 可在网页端调整. 设置权限了之后,只允许权限等级超过的群员报名."
    if context['message'] in ['设置报名权限']: return text
    a = context['message'].replace('设置报名权限', '').strip().split(' ')
    if not (len(a) == 2 and a[0].isdigit() and a[1].isdigit()): return text
    teams = Team().getByGroup(group)
    teamNum = int(a[0])
    if teamNum > len(teams) or teamNum < 1: return f"没有编号为{teamNum}的团"
    teams[teamNum - 1].setSign(a[1])
    await sendData(group.group, context['info']['bot'], getTeamDetail(teams[teamNum-1]))
    return f"团队权限修改成功回复 查看团队 {teamNum} 即可查看"



