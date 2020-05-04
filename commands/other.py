#!/usr/bin/env python
# encoding: utf-8

from models import Group
import datetime

async def handle_invite(context):
    bot = context['bot']
    group = await Group.get_or_none(group=str(context['group_id']))
    if not group:
        reply = '请联系QQ986859110购买群权限后邀请进群'
        await bot.set_group_add_request(flag=context['flag'], sub_type='invite', approve=False, reason=reply, self_id=context['self_id'])
        return await bot.send_private_msg(user_id=context['user_id'], self_id=context['self_id'], message=reply)
    today = datetime.date.today()
    if group.expire < today:
        reply = '群权限已过期, 请联系QQ986859110购买群权限后邀请进群'
        await bot.set_group_add_request(flag=context['flag'], sub_type='invite', approve=False, reason=reply,
                                        self_id=context['self_id'])
        return await bot.send_private_msg(user_id=context['user_id'], self_id=context['self_id'], message=reply)

    group.robot = str(context['self_id'])
    await group.save()
    return await bot.set_group_add_request(flag=context['flag'], sub_type='invite', approve=True, self_id=context['self_id'])