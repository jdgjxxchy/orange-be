#!/usr/bin/env python
# encoding: utf-8

from models import Group, User
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


async def refresh_group_member(context, bot):
    qq_group = await Group.get(group=context['group_id'])
    if context['user_id'] == context['self_id'] and context['notice_type'] == 'group_decrease':
        # await User.filter(group=qq_group).delete()
        return
    if not qq_group:
        return
    now = datetime.date.today()
    expire = qq_group.expire
    if now > expire:
        return
    member_list = await bot.get_group_member_list(group_id=context['group_id'])
    member_id_list = list(map(lambda x: str(x['user_id']), member_list))
    qq_group = await Group.get(group=context['group_id'])
    member_object_list = await User.filter(group_id=qq_group.id).all()
    member_object_id_list = list(map(lambda x: x.qq, member_object_list))
    for member in member_list:
        if str(member['user_id']) not in member_object_id_list:
            user_other = await User.filter(qq=member['user_id'], group=qq_group)
            if len(user_other) > 1:
                for delete_user in user_other[1:]:
                    await delete_user.delete()
            role = '0011'
            if member['role'] == 'admin':
                role = '1111'
            if member['role'] == 'owner':
                role = '2111'
            if not user_other:
                name = member['nickname'] or member['card']
                try:
                    await User.create(
                        qq=str(member['user_id']),
                        name=member['nickname'] or member['card'],
                        group=qq_group,
                        auth=role,
                    )
                except:
                    await bot.send_private_msg(user_id=986859110, self_id=context['self_id'], message=f'{qq_group}群的{name}录入失败,')
                    pass
    for member_object in member_object_list:
        if member_object.qq not in member_id_list:
            await member_object.delete()


