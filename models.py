#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: models.py
@time: 2020/1/7

"""

from tortoise import Model, fields

blank = '[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]'

class BaseModel(Model):
    id = fields.IntField(pk=True)



class Group(BaseModel):

    group = fields.CharField(max_length=20, unique=True)
    name = fields.CharField(max_length=100)
    robot = fields.CharField(max_length=20)
    expire = fields.DateField()
    recover_at = fields.DateField(null=True, default=None)
    maxTeam = fields.IntField(default=3)
    maxTemplate = fields.IntField(default=2)
    maxQA = fields.IntField(default=2)


    class Meta:
        table = "group"



class User(BaseModel):

    qq = fields.CharField(max_length=20, index=True)
    name = fields.CharField(max_length=100)
    group = fields.ForeignKeyField('models.Group', related_name='users')
    # 0011 1. 群里权限, 2. 是否可以操作团队 3. 报名权限 4. 登记老板权限
    auth = fields.CharField(max_length=20, default='0011')

    absent = fields.IntField(default=0)
    tip = fields.CharField(max_length=200, null=True) # 团长的备注
    token = fields.CharField(max_length=30, unique=True, null=True)
    password = fields.CharField(max_length=100, default=123456)


    class Meta:
        table = "user"



class Team(BaseModel):

    qq = fields.CharField(max_length=100)
    name = fields.CharField(max_length=100)
    members = fields.CharField(max_length=5000, default=blank)
    alternate = fields.CharField(max_length=5000, default='[]')
    startTime = fields.CharField(max_length=100)
    tip = fields.CharField(max_length=100, default='')
    sign = fields.IntField(default=1)
    group = fields.ForeignKeyField("models.Group", related_name="teams")
    delete_at = fields.DatetimeField(null=True, default=None)
    create_at = fields.DatetimeField(auto_now_add=True)
    update_at = fields.DatetimeField(auto_now=True)




class Template(BaseModel):
    qq = fields.CharField(max_length=100)
    name = fields.CharField(max_length=100)
    members = fields.CharField(max_length=5000, default=blank)
    group = fields.ForeignKeyField("models.Group", related_name='templates')


    class Meta:
        table = 'template'



class Gold(BaseModel):

    __tablename__ = 'gold'
    area = fields.CharField(max_length=20, index=True)
    url5173 = fields.CharField(max_length=200)
    urlOfficial = fields.CharField(max_length=200)
    urlPost = fields.CharField(max_length=200)
    gold = fields.CharField(max_length=1000, null=True)
    update_at = fields.DatetimeField(auto_now=True)


    class Meta:
        table = 'gold'



class Hong(BaseModel):

    group = fields.CharField(max_length=20, index=True)
    qq = fields.CharField(max_length=20, index=True)
    occu = fields.CharField(max_length=20, index=True)
    content = fields.CharField(max_length=2000)


    class Meta:
        table = 'hong'

    @staticmethod
    async def setHong(qq, group, occu, content):
        hong = await Hong.get_or_none(group=group, occu=occu)
        if hong:
            if hong.content != content:
                hong.qq = qq
                hong.content = content
                await hong.save()
                return "修改成功"
            return ""
        else:
            await Hong.create(qq=qq, group=group, occu=occu, content=content)
            return "新增成功"



class CustomQA(BaseModel):

    group = fields.ForeignKeyField("models.Group", related_name="qas")
    question = fields.CharField(max_length=200, index=True)
    answer = fields.CharField(max_length=200)


    class Meta:
        table = 'custom'



class Gap(BaseModel):

    group = fields.CharField(max_length=20, unique=True)
    hong = fields.IntField(null=True)
    sethong = fields.IntField(null=True)
    monitor = fields.IntField(null=True)
    yao = fields.IntField(null=True)
    editName = fields.IntField(null=True)
    gold = fields.IntField(null=True)
    func = fields.IntField(null=True)
    customQA = fields.IntField(null=True)


    class Meta:
        table = 'gap'