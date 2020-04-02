#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: models.py
@time: 2020/1/7

"""
from main import db
from sqlalchemy import or_, and_, not_
import datetime

blank = '[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]'

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    robot = db.Column(db.String(20), nullable=False)
    expire = db.Column(db.Date, nullable=False)
    users = db.relationship("User", backref='group', lazy='dynamic')
    teams = db.relationship("Team", backref='group', lazy='dynamic')
    templates = db.relationship("Template", backref='group', lazy='dynamic')
    customs = db.relationship("CustomQA", backref='group', lazy='dynamic')
    recover_at = db.Column(db.Date, nullable=True, default=None)
    # owner = db.Column(db.Integer, nullable=True)
    maxTeam = db.Column(db.Integer, nullable=False, default=3)
    maxTemplate = db.Column(db.Integer, nullable=False, default=2)
    maxQA = db.Column(db.Integer, nullable=False, default=2)

    def __init__(self, **kwargs):
        try:
            for name, value in kwargs.items():
                setattr(self, name, value)
        except:
            pass

    def getByGroup(self, group):
        return self.query.filter_by(group=group).first()

    def changeName(self, name):
        self.name = name
        self.save()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def __repr__(self):
        return f'<Group group: {self.group}, expire: {self.expire}>'

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(20), index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    auth = db.Column(db.String(20), nullable=False, default='0011')
    absent = db.Column(db.Integer, nullable=False, default=0)
    tip = db.Column(db.String(100), nullable=True) #团长的备注
    # 0011 1. 群里权限, 2. 是否可以操作团队 3. 报名权限 4. 登记老板权限
    token = db.Column(db.String(30), unique=True, nullable=True)
    password = db.Column(db.String(20), nullable=False, default='123456')


    def __init__(self, **kwargs):
        try:
            for name, value in kwargs.items():
                setattr(self, name, value)
        except:
            pass

    def getByQG(self, qq, group):
        return self.query.filter_by(qq=qq, group=group).first()

    def getByQQ(self, qq):
        return self.query.filter_by(qq=qq).all()

    def getByGroup(self, group):
        return self.query.filter_by(group=group).all()

    def getById(self, id):
        return self.query.filter_by(id=id).first()

    def getByToken(self, token):
        return self.query.filter_by(token=token).first()

    def changeName(self, name):
        self.name = name
        db.session.commit()


    def changeOtherName(self, qq, group, name):
        self.query.filter_by(qq=qq, group=group).update({'name': name})
        db.session.commit()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def __repr__(self):
        return f'<User QQ: {self.qq}, name: {self.name}>'

class Team(db.Model):
    __tablename__ = "team"
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    members = db.Column(db.String(5000), default=blank)
    alternate = db.Column(db.String(5000), default='[]')
    startTime = db.Column(db.String(100), nullable=True)
    tip = db.Column(db.String(100), default='')
    sign = db.Column(db.Integer, default=1)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    delete_at = db.Column(db.DateTime, index=True, nullable=True, default=None)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, **kwargs):
        try:
            for name, value in kwargs.items():
                setattr(self, name, value)
        except:
            pass

    def getByGroup(self, group):
        return self.query.filter_by(group=group, delete_at=None).all()

    def getById(self, id):
        return self.query.filter_by(id=id, delete_at=None).first()

    def getDel(self, group):
        return self.query\
            .filter(and_(Team.group==group, not_(Team.delete_at==None)))\
            .order_by(Team.delete_at.desc()).limit(3)\
            .all()

    def recover(self, id):
        self.query.filter_by(id=id).update({"delete_at": None})
        db.session.commit()

    def setTip(self, tip):
        self.tip = tip
        self.save()

    def setSign(self, sign):
        self.sign = sign
        self.save()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def __repr__(self):
        return f'<Team name={self.name} startTime={self.startTime}>'

class Template(db.Model):
    __tablename__ = "template"
    id = db.Column(db.Integer, primary_key=True)
    qq = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    members = db.Column(db.String(5000), default=blank)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))


    def __init__(self, **kwargs):
        try:
            for name, value in kwargs.items():
                setattr(self, name, value)
        except:
            pass

    def getByGroup(self, group):
        return self.query.filter_by(group=group).all()

    def getById(self, id):
        return self.query.filter_by(id=id).first()

    def deleteById(self, id):
        self.query.filter_by(id=id).delete()
        db.session.commit()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

    def __repr__(self):
        return f'<Template >'

class Gold(db.Model):

    __tablename__ = 'gold'
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(20), index=True, nullable=False)
    url5173 = db.Column(db.String(200), nullable=True)
    urlOfficial = db.Column(db.String(50), nullable=True)
    urlPost = db.Column(db.String(200), nullable=True)
    gold = db.Column(db.String(1000), nullable=True)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def getGoldByArea(self, area):
        return self.query.filter_by(area=area).first()

    def add(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()

class Hong(db.Model):

    __tablename__ = "hong"
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), index=True, nullable=False)
    qq = db.Column(db.String(20), index=True, nullable=False)
    occu = db.Column(db.String(20), index=True, nullable=False)
    content = db.Column(db.String(2000), nullable=False)

    def __init__(self, **kwargs):
        try:
            for name, value in kwargs.items():
                setattr(self, name, value)
        except:
            pass

    def setHong(self, qq, group, occu, content):
        hong = self.query.filter_by(group=group, occu=occu).first()
        if hong:
            if hong.content != content:
                hong.qq = qq
                hong.content = content
                db.session.commit()
                return "修改成功"
            return ""
        else:
            self.qq = qq
            self.group = group
            self.occu = occu
            self.content = content
            db.session.add(self)
            db.session.commit()
            return "新增成功"

    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def getByOccu(self, occu, group='0'):
        return self.query\
            .filter(and_(Hong.occu==occu, or_(Hong.group == group, Hong.group=='0')))\
            .order_by(db.desc(Hong.group))\
            .all()

    def getByGroup(self, group, occu):
        return self.query.filter_by(group=group, occu=occu).first()

    def __repr__(self):
        return f'<Hong occu: {self.occu} group: {self.group}>'

class CustomQA(db.Model):

    __tablename__ = 'custom'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    question = db.Column(db.String(200), nullable=False, index=True)
    answer = db.Column(db.String(200), nullable=False)

    def getByGroup(self, group):
        return self.query.filter_by(group=group).all()



class Gap(db.Model):

    __tablename__ = 'gap'
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), unique=True, nullable=False)
    hong = db.Column(db.Integer, nullable=True)
    sethong = db.Column(db.Integer, nullable=True)
    monitor = db.Column(db.Integer, nullable=True)
    yao = db.Column(db.Integer, nullable=True)
    editName = db.Column(db.Integer, nullable=True)
    gold = db.Column(db.Integer, nullable=True)
    func = db.Column(db.Integer, nullable=True)
    customQA = db.Column(db.Integer, nullable=True)

    def find(self, group):
        res = self.query.filter_by(group=group).first()
        if not res:
            self.group = group
            db.session.add(self)
            db.session.commit()
            res = self
        return res

    def setTime(self, cmd, sec):
        setattr(self, cmd, sec)
        db.session.commit()


def init():
    import pymysql
    con = pymysql.Connect(
        host='47.101.173.121',
        port=3306,
        user='root',
        password='Hpxt2020hpxt!',
        database='orange'
    )
    cur = con.cursor()
    cur.execute('select * from usetime where limitTime > "2020-3-6"')
    res = cur.fetchall()
    for i in res:
        cur.execute('select teamName, mostTeam from teamgrid_qqgroup where groupNumber = %s', [i[1]])
        r = cur.fetchone()
        if r:
            name = r[0]
            teams = r[1]
        else:
            name = i[1]
            teams = 3
        Group(group=i[1],name=name,expire=i[2],robot='0',maxTeam=teams).add()


def init2():
    now = datetime.date.today() + datetime.timedelta(days=30)
    Group(group='1063943569', name='实验', expire=now, robot='191859298').add()
    Gold(area='华乾',url5173='http://s.5173.com/jx3-5ootfk-1got2e-2nzyqv-0-kb0ewi-0-0-0-a-a-a-a-a-0-0-0-0.shtml',
         urlPost='https://tieba.baidu.com/p/6522135011',
         urlOfficial='z05|gate0514').add()

def init3():
    groups = Group().query.all()
    now =datetime.date.today()
    for i in groups:
        expire = i.expire
        days = (expire - now).days
        if days > 100:
            i.expire = i.expire + datetime.timedelta(days=30)
            i.save()
            print(i)
    print(groups)

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    # init()
    init3()
