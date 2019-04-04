# -*- coding: utf-8 -*-
# @Time : 2019/4/1
# @Author : zxy

import asyncio
from logger.log import storage_log
from motor.motor_asyncio import AsyncIOMotorClient
from config.config import *

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class MotorOperation():
    def __init__(self, db_configs=DEFAULT_DB_CONFIG):
        self.__dict__.update(**db_configs)
        if self.user:
            self.motor_uri = f"mongodb://{self.user}:{self.passwd}@{self.host}:{self.port}/{self.auth_db}?authSource={self.auth_db}"
        else:
            self.motor_uri = f"mongodb://{self.host}:{self.port}/{self.db_name}"
        self.client = AsyncIOMotorClient(self.motor_uri)
        self.mb = self.client[self.db_name]

    async def add_index(self, col, index_name):
        '''
        添加索引
        :param col: 集合
        :param index_name: 索引名（即要添加为索引的字段）
        '''
        await self.mb[col].create_index(index_name)

    async def get_new_items_list(self, ori_items):
        '''
        过滤已存在数据，获取新item列表
        '''
        id_list = [item['house_id'] for item in ori_items]
        exist_items = self.mb[COLLECTION_SHPersonalHouse].find(
            {'house_id': {'$in': id_list}})
        exist_ids = [item['house_id'] async for item in exist_items]

        return [item for item in ori_items if item['house_id'] not in exist_ids]

    async def save_data(self, items, col, key):
        '''
        保存数据
        :param items: 数据项->单条或多条
        :param col:集合
        :param key:主键
        :return:
        '''
        if isinstance(items, list):
            for item in items:
                try:
                    await self.mb[col].update_one({
                        key: item.get(key)},
                        {'$set': item},
                        upsert=True)
                    storage_log.debug(f"数据插入成功:{item}")
                except Exception as e:
                    storage_log.error(f"数据插入出错:{e.args}此时的item是:{item}")
        elif isinstance(items, dict):
            try:
                await self.mb[col].update_one({
                    key: items.get(key)},
                    {'$set': items},
                    upsert=True)
                storage_log.debug(f"数据插入成功:{items}")
            except Exception as e:
                storage_log.error(f"数据插入出错:{e.args}此时的item是:{items}")
