# -*- coding: utf-8 -*-
# @Time : 2019/4/1
# @Author : zxy

import asyncio
import aiohttp
from logger.log import crawler_log
import async_timeout
from collections import namedtuple
from config.config import *
from typing import Optional
from async_retrying import retry
from lxml import html
from aiostream import stream
from utils import proxy_helper
import marshal
import random


Response = namedtuple("Response",
                      ["status", "source"])

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

sem = asyncio.Semaphore(CONCURRENCY_NUM)


class Crawler():
    def __init__(self):
        self.session = None
        self.tc = None

    async def bound_get_session(self, url, _kwargs: dict = {}, source_type="text", status_code=200) -> Response:
        async with sem:
            res = await self.get_session(url, _kwargs, source_type, status_code)
            await asyncio.sleep(random.random())
            return res

    @retry(attempts=MAX_RETRY_TIMES)
    async def get_session(self, url, _kwargs: dict = {}, source_type="text", status_code=200) -> Response:
        '''
        :param kwargs:url,headers,data,params,etc,,
        :param method: get post.
        :param timeout: defalut 5s.
        '''
        # 使用marshal复制提高性能
        kwargs = marshal.loads(marshal.dumps(_kwargs))

        if USE_PROXY:
            kwargs["proxy"] = await self.get_proxy()
        method = kwargs.pop("method", "get")
        timeout = kwargs.pop("timeout", 5)
        encoding = kwargs.pop("encoding", None)
        with async_timeout.timeout(timeout):
            async with getattr(self.session, method)(url, **kwargs) as req:
                status = req.status
                if status in [status_code, 201]:
                    if source_type == "text":
                        source = await req.text(encoding=encoding,errors='ignore') if encoding else await req.text()
                    elif source_type == "buff":
                        source = await req.read()

        crawler_log.debug(f"get url:{url},status:{status}")
        res = Response(status=status, source=source)
        return res

    def xpath(self, _response, rule, _attr=None,clean_method=None):
        if isinstance(_response, Response):
            source = _response.text
            root = html.fromstring(source)

        elif isinstance(_response, str):
            source = _response
            root = html.fromstring(source)
        else:
            root = _response
        nodes = root.xpath(rule)

        if _attr:
            if _attr == "text":
                result = [entry.text for entry in nodes]
            else:
                result = [entry.get(_attr) for entry in nodes]
        else:
            result = nodes

        if clean_method:
            result[0] = clean_method(result[0])

        return result

    async def branch(self, coros, limit=10):
        '''
        使用aiostream模块对异步生成器做一个切片操作。这里并发量为10.
        :param coros: 异步生成器
        :param limit: 并发次数
        :return:
        '''
        index = 0
        while True:
            xs = stream.preserve(coros)
            ys = xs[index:index + limit]
            t = await stream.list(ys)
            if not t:
                break
            await asyncio.ensure_future(asyncio.wait(t))
            index += limit + 1

    async def get_proxy(self) -> Optional[str]:
        '''
        获取代理
        '''
        while True:
            proxy = await proxy_helper.get_proxy()
            if proxy:
                host = proxy[0].get('ip')
                port = proxy[0].get('port')
                ip = f"http://{host}:{port}"
                return ip
            else:
                crawler_log.info("代理超时开始等待")

                await asyncio.sleep(5)

    async def init_session(self):
        '''
        创建Tcpconnector，包括ssl和连接数的限制
        创建一个全局session。
        :return:
        '''
        self.tc = aiohttp.connector.TCPConnector(limit=300, force_close=True,
                                                 enable_cleanup_closed=True,
                                                 verify_ssl=False)
        self.session = aiohttp.ClientSession(connector=self.tc)

    async def close(self):
        await self.tc.close()
        await self.session.close()
