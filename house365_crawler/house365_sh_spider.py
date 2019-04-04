# -*- coding: utf-8 -*-
# @Time : 2019/4/1
# @Author : zxy

from common.base_crawler import Crawler
from db.mongo_helper import MotorOperation
from logger.log import crawler_log, parser_log
from utils.xpath_helper import SH_XPATH_DICT
from config.config import *
from decorators.decorators import execute_time
import asyncio
import re
import time
from itertools import chain
from functools import partial


class House365ShSpider(Crawler):
    def __init__(self, cities):
        self.cities = cities
        super().__init__()
        self.list_base_url = 'http://{city}.sell.house365.com/district_i1/dl_p{page}.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }

        self._selector = None
        self.motor = MotorOperation()

    async def get_max_page(self, city):
        '''
        获取最大页码
        '''
        self._selector = SH_XPATH_DICT[city]
        if city in SPECIAL_CITIES:
            max_page = await self.get_max_page_for_special(city)
            return max_page

        url = self.list_base_url.format(city=city, page=1)
        kwargs = {'headers': self.headers, 'encoding': 'gbk'}

        response = await self.get_session(url, kwargs)
        if response.status == 200:
            source = response.source
            max_page = self.xpath(
                source,
                self._selector.max_page,
                clean_method=partial(
                    self.data_clean,
                    clean_type=f'{city}_max_page'))
            if max_page and max_page[0].isdigit():
                return int(max_page[0])

    async def get_max_page_for_special(self, city):
        '''
        为特殊城市获取最大页码
        '''
        ori_page = 50
        kwargs = {'headers': self.headers, 'encoding': 'gbk'}

        while True:
            url = self.list_base_url.format(city=city, page=ori_page)
            response = await self.get_session(url, kwargs)
            if response.status == 200:
                source = response.source
                max_page = self.xpath(source, self._selector.max_page)

                if max_page and max_page[0].isdigit():
                    max_page = int(max_page[0])
                    if max_page < ori_page:
                        return max_page
                    else:
                        ori_page += 50

    async def fetch_list(self, city, page):
        '''
        抓取列表页
        :param page: 页码
        '''
        url = self.list_base_url.format(city=city, page=page)
        kwargs = {'headers': self.headers, 'encoding': 'gbk'}
        response = await self.bound_get_session(url, kwargs)
        if response.status == 200:
            items = await self.parse_list(response.source, city)
            crawler_log.info(f'第{page}页:{items}')
            return items

    async def parse_list(self, source, city):
        '''
        解析列表页
        :param source: 页面源码
        :param city: 城市
        '''
        items = []
        info_list = self.xpath(source, self._selector.info_list)
        for info in info_list:
            house_url = info.xpath(self._selector.house_url)[0]
            title = self.data_clean(
                info.xpath(
                    self._selector.title)[0],
                clean_type='title')
            items.append({
                'house_id': re.search('s_(\d+).html', house_url).group(1),
                'house_url': house_url,
                'title': title,
                'city': city,
            })

        return items

    async def fetch_detail(self, item):
        '''
        抓取详情页
        :param item: 数据项
        '''
        url = item['house_url']
        kwargs = {'headers': self.headers, 'encoding': 'gbk'}

        response = await self.bound_get_session(url, kwargs)
        if response.status == 200:
            await self.parse_detail(response.source, item)

    async def parse_detail(self, source, item):
        '''
        解析详情页
        :param source: 页面源码
        :param item: 数据项
        '''
        try:
            item['name'] = self.xpath(
                source, self._selector.name, clean_method=partial(
                    self.data_clean, clean_type='name'))[0]
            item['phone'] = self.xpath(
                source, self._selector.phone, clean_method=partial(
                    self.data_clean, clean_type='phone'))[0]
            await self.save_data(item)

        except Exception as e:
            parser_log.error(f'item:{item} error:{e}')

    def data_clean(self, data, clean_type):
        '''
        数据清洗
        :param data: 数据内容
        :param clean_type: 清洗类型
        '''
        if clean_type in MAX_PAGE_CLEAN_TYPE:
            return re.search(r'\d+/(\d+)', data).group(1)

        if clean_type == 'title':
            return re.sub('[\\r\\n\\t\\s]', '', data)

        if clean_type == 'name':
            return re.sub('[\\r\\n\\t]', '', data)

        if clean_type == 'phone':
            return data.replace(' ', '')

        return data

    async def save_data(self, item):
        '''
        保存数据
        :param item: 数据项
        '''
        item['crawl_time'] = time.time()
        await self.motor.save_data(item, COLLECTION_SHPersonalHouse, 'house_id')

    async def filter_items_list(self, items_list):
        '''
        合并items_list为一个大列表，并查询数据库进行过滤
        '''
        merged_list = list(chain.from_iterable(items_list))
        filtered = await self.motor.get_new_items_list(merged_list)
        return filtered

    async def run(self):
        await self.init_session()
        crawler_log.info('开始'.center(50, '-'))
        crawler_log.info(f'待爬城市数:{len(self.cities)}')

        for i, city in enumerate(self.cities):
            max_page = await self.get_max_page(city)
            crawler_log.info(f'正在爬取：{city} 最大页码：{max_page}')

            list_tasks = [
                asyncio.ensure_future(
                    self.fetch_list(
                        city,
                        page)) for page in range(
                    1,
                    max_page + 1)]
            items_list = await asyncio.gather(*list_tasks)

            filtered_items = await self.filter_items_list(items_list)
            crawler_log.info(f'{city} 过滤后待爬取的详情数为：{len(filtered_items)}')

            detail_tasks = [
                asyncio.ensure_future(
                    self.fetch_detail(item)) for item in filtered_items]
            await asyncio.gather(*detail_tasks)

            crawler_log.info(f'剩余城市数:{len(self.cities) - (i + 1)}')

        crawler_log.info('结束'.center(50, '-'))

    @execute_time(unit='m')
    def start(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run())
        except Exception as e:
            crawler_log.error(e)
        finally:
            loop.close()


if __name__ == '__main__':
    spider = House365ShSpider(SH_AVAILABLE_CITIES)
    spider.start()
