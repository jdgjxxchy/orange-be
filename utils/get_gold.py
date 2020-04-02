#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: get_gold.py
@time: 2019/10/22

"""
import re
import asyncio
import time
import json
from models import Gold
from pyquery import PyQuery as pq
from main import db


def parse5173(content):
    if content == 'error':
        return []
    gold = re.findall('<li><b>1元=(\d+.\d*)</b>金', content)
    gold = list(map(float, gold))
    gold.sort(reverse=True)
    return list(map(int, gold[:5]))


async def getLastUrl(req, url):
    content = await req.get_http(url)
    if content == 'error':
        return ''
    try:
        urlLast = re.search(r'<a href=".*?pn=(\d+)">尾页</a>', content).group(1)
        base_url = url.split('?')[0]
        urlList = []
        for pages in range(int(urlLast) + 1):
            url = base_url + '?pn=' + str(pages)
            urlList.append(url)
        return urlList
    except:
        return ''


def parsePost(content):
    if content == 'error':
        return []
    posts = []
    doc = pq(content)
    for i in doc('.d_post_content').items():
        try:
            gold = int(re.search('(\d\d\d\d*).*?出', i.text(), re.S).group(1))
            if gold < 2000 and gold > 300:
                posts.append(gold)
        except:
            pass
    return posts

async def parseTieba(req, url):
    urls = await getLastUrl(req, url)
    if urls == '':
        return []
    posts = []
    if urls[-2]:
        posts.extend(parsePost(await req.get_http(urls[-2])))
    posts.extend(parsePost(await req.get_http(urls[-1])))
    posts = posts[-6:]
    posts.sort()
    return posts

async def parseOfficial(req, data):
    if not data:
        return []
    url = 'https://api-wanbaolou.xoyo.com/api/buyer/goods/list'
    zone_id, server_id = data.split('|')
    params = {
        "zone_id": zone_id,
        "server_id": server_id,
        "sort[single_count_price]": 0,
        "game": 'jx3',
        "page": 1,
        "size": 10,
        "__ts__": int(time.time())
    }
    money = []
    res = json.loads(await req.get_http(url, params))
    if 'list' not in res['data']:
        return []
    for i in res['data']['list']:
        money.append(i['single_count_price'])

    return money[:5]


async def get_gold(req, area):
    gold = Gold().getGoldByArea(area)
    if gold is None:
        return
    res = {}
    url5173 = gold.url5173
    urlPost = gold.urlPost
    urlOfficial = gold.urlOfficial
    res['5173'] = parse5173(await req.get_http(url5173))
    res['post'] = await parseTieba(req, urlPost)
    res['official'] = await parseOfficial(req, urlOfficial)
    gold = Gold().getGoldByArea(area)
    gold.gold = json.dumps(res, ensure_ascii=False)
    gold.save()

if __name__ == '__main__':
    from utils.Request import Request
    req = Request()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_gold(req, '华乾'))
    del req
