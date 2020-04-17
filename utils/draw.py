#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: draw.py
@time: 2020/1/20

"""

import json
import base64

from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from models import User
from utils.dicts import colorDic, imgDic, occuList

class Canvas():

    font1 = ImageFont.truetype("./src/wei.ttf", 24)
    font2 = ImageFont.truetype("./src/wei.ttf", 12)
    font3 = ImageFont.truetype("./src/wei.ttf", 30)
    font4 = ImageFont.truetype("./src/wei.ttf", 20)

    imgSource = [
        Image.open('./src/hj.png'), # 花间
        Image.open('./src/lj.png'), # 奶花
        Image.open('./src/bx.png'), # 冰心
        Image.open('./src/yc.png'), # 奶秀
        Image.open('./src/yj.png'), # 易筋
        Image.open('./src/xs.png'), # 洗髓
        Image.open('./src/qc.png'), # 气纯
        Image.open('./src/jc.png'), # 剑纯
        Image.open('./src/ax.png'), # 傲雪
        Image.open('./src/tct.png'), # 铁牢
        Image.open('./src/cj.png'), # 藏剑
        Image.open('./src/dj.png'), # 毒经
        Image.open('./src/bt.png'), # 奶毒
        Image.open('./src/jy.png'), # 惊羽
        Image.open('./src/tl.png'), # 天罗
        Image.open('./src/fy.png'), # 焚影
        Image.open('./src/mz.png'), # 明尊
        Image.open('./src/xc.png'), # 丐帮
        Image.open('./src/fs.png'), # 分山
        Image.open('./src/tg.png'), # 铁骨
        Image.open('./src/mw.png'), # 莫问
        Image.open('./src/xz.png'), # 奶歌
        Image.open('./src/bd.png'), # 霸刀
        Image.open('./src/pl.png'), # 蓬莱
        Image.open('./src/lx.png'), # 凌雪

    ]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        # self.canvas = Image.new('RGB', (width * 5 + 5, height * 5 + 5), '#fff')
        self.left = 48
        self.top = 85
        self.canvas = Image.new("RGB", [1100, 550], (233, 233, 233))
        self.draw = ImageDraw.Draw(self.canvas)
        self.alpha = Image.new('L', self.canvas.size, 255)
        for i in range(0, 6):
            self.draw.line([width * i + self.left, self.top, width * i + self.left, height * 5 + self.top], '#000')
            self.draw.line([self.left, height * i + self.top, width * 5 + self.left, height * i + self.top], '#000')

    def rec(self, size, radii):
        # 画圆（用于分离4个角）
        circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

        w, h = size

        # 画4个角（将整圆分离为4个部分）
        alpha = Image.new('L', size, 255)
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
        alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
        alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角

        return alpha

    def setPlayer(self, num, occu, name, clientCall, isDouble):
        x = num % 5 * self.width
        y = num // 5 * self.height
        name2 = clientCall + '喊的老板' if clientCall else ''
        color = colorDic[occuList[occu]]
        size =  [self.width-1, self.height-1]
        imgSize = [25,25]
        rec = Image.new("RGB", size, color)
        self.canvas.paste(rec, (x + self.left + 1, y + self.top + 1), self.rec(size,10))
        img = self.imgSource[occu].resize(imgSize).convert("RGBA")
        self.canvas.paste(img, (x + self.left + 3, y + self.top + 3), self.rec(imgSize, 13))
        self.draw.text((x + self.left, y + self.top + 10), name.center(28 - len(name) * 2), "#000", font=self.font1)
        self.draw.text((x + self.left, y + self.top + 50), name2.center(50 - len(name2) * 2), "#000", font=self.font2)
        if isDouble:
            self.draw.text((x + self.left +self.width - 25, y + self.top), '双', "#000", font=self.font4)

    def setOccus(self, index, ol):
        x = index % 5 * self.width
        y = index // 5 * self.height
        imgSize = [21, 21]
        for num, i in enumerate(ol):
            ii = num % 9
            jj = num // 9
            img = self.imgSource[i].resize(imgSize).convert("RGBA")
            self.canvas.paste(img, (x + self.left + 3 + ii * 22, y + self.top + 3 + jj * 22), self.rec(imgSize, 13))

    def setTitle(self, title):
        ImageDraw.Draw(self.canvas).text((self.left, 20), title.center(120 - len(title) * 2), (0, 0, 0), font=self.font3)

    def setTip(self, tip):
        if tip:
            ImageDraw.Draw(self.canvas).text((self.left, 500), '团队备注:' + tip, (25, 25, 112), font=self.font4)


def imageToBase64(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    byte_data = img_buffer.getvalue()
    return  base64.b64encode(byte_data).decode()

def fileToBase64(url):
    img = Image.open(url)
    return imageToBase64(img)

def drawTeam(team, group):
    i = 0
    members = json.loads(team.members)
    title = team.startTime + '  ' + group.name + '团  ' + team.name
    img = Canvas(200, 80)
    img.setTip(team.tip)
    group.save()
    for dic in members:
        if 'occu' not in dic and 'occuList' not in dic :
            i += 1
            continue
        name = ''
        if 'player' in dic:
            if 'id' in dic['player']:
                user = User().getById(dic['player']['id'])
                if user: nickname = user.name
                else: nickname = '已删除群员'
            elif 'name' in dic['player']:
                nickname = dic['player']['name']
            else:
                nickname = ''
            name = nickname[:6] if len(nickname) > 6 else nickname
        name2 = ''
        if 'client' in dic:
            if 'whose' in dic['client']:
                user = User().getById(dic['client']['whose'])
                nickname = user.name
            else:
                nickname = ''
            name2 = nickname[:6] if len(nickname) > 6 else nickname
        isDouble = 'double' in dic and dic['double'] or ('mustDouble' in dic)
        if 'occu' in dic or ('occuList' in dic and len(dic['occuList']) == 1):
            occu = dic['occu'] if 'occu' in dic else dic['occuList'][0]
            img.setPlayer(i, occu, name, name2, isDouble)
        else:
            img.setOccus(i, dic['occuList'])
        i += 1
    img.setTitle(title)
    str = imageToBase64(img.canvas)
    s = f'[CQ:image,file=base64://{str}]'
    url = 'https://orange.arkwish.com'
    s += '修改昵称 XXX 修改自己昵称(中间加空格)\n修改团名 XXX 修改团队名称\n' \
         '模板设置及调队等更多功能复制到浏览器 ' + url
    return s
