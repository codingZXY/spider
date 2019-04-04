# -*- coding: utf-8 -*-
# @Time : 2019/4/1
# @Author : zxy

from functools import wraps
from logger.log import crawler_log
import traceback
import time


def func_log(f=True):
    '''
    函数日志装饰
    :param f:默认是不输出info，False的时候输出info信息。
    :return:
    '''
    def flag(func):
        @wraps(func)
        def log(*args, **kwargs):
            try:
                if f:
                    crawler_log.info(f"{func.__name__} is run")
                return func(*args, **kwargs)
            except Exception as e:
                crawler_log.error(f"{func.__name__} is error,here are details:{traceback.format_exc()}")

        return log

    return flag

def execute_time(unit='s'):
    '''
    函数执行时间
    :param unit:默认单位是秒。
    '''
    def flag(func):
        @wraps(func)
        def execute_time(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()

            if unit == 's':
                cost = f'{end - start} seconds'
            elif unit == 'm':
                cost = f'{(end - start)/60} minutes'
            elif unit == 'h':
                cost = f'{(end - start)/3600} hours'

            print(f'Func Name:{func.__name__} Execute Time: {cost}')

            return result

        return execute_time

    return flag

