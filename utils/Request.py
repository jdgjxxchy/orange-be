#!/usr/bin/env python
# encoding: utf-8

"""
@version:
@author: Wish Chen
@contact: 986859110@qq.com
@file: Request.py
@time: 2019/10/22

"""
import aiohttp
import asyncio

class Request:

    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(headers=headers)

    async def post_http(self, url, data):
        try:
            async with self.session.post(url, data=data) as res:
                return await res.text()
        except:
            return "error"

    async def get_http(self, url, params=''):

        try:
            async with self.session.get(url, params=params, timeout=self.timeout) as res:
                return await res.text()
        except:
            return "error"

    def __del__(self):
        asyncio.ensure_future(self.exit())

    async def exit(self):
        await self.session.close()

async def main():
    req = Request()
    s = await req.get_http("http://s.5173.com/jx3-0-iw0yxb-hczhmz-0-kb0ewi-0-0-0-a-a-a-a-a-0-0-0-0.shtml")
    print(s)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
