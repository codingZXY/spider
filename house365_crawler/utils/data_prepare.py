# -*- coding: utf-8 -*-
# @Time : 2019/4/4
# @Author : zxy
import requests
import re
import time

from config.config import CITIES_DICT
from lxml import etree
from utils.xpath_helper import SH_XPATH_DICT


def get_cities():
    '''
    获取城市字典
    '''
    url = 'http://stat.house365.com/ga_config.js?t=7'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'
    results = re.findall(r'conf_ga_city\[".*"\] = ".*";', res.text)
    cities = {}
    for r in results:
        s = re.search(r'conf_ga_city\["(.*)"\] = "(.*)";', r)
        cities[s.group(1)] = s.group(2)

    print(cities)

def get_sh_xpath_dict():
    '''
    获取二手房xpath选择器字典
    通过该方法可知
    哪些城市是现有Xpath能满足的
    哪些城市是需要添加Xpath解析的
    哪些城市是未加盟的

    分析need_parse列表，为需要添加Xpath解析的城市添加Xpath，最后将Xpath Dict维护至xpath_helper中
    '''
    url = 'http://{city}.sell.house365.com/district_i1/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    xpath_dict = {}
    not_available = []
    need_parse = []

    for city in CITIES_DICT.keys():
        print(f'Checking City:{city}')
        response = requests.get(url.format(city=city), headers=headers)
        if response.url == 'http://meng.house365.com':
            not_available.append(city)
            continue

        response.encoding = 'gbk'
        html = etree.HTML(response.text)

        if html.xpath('//div[@id="qy_list_cont"]/div[@class="info_list"]'):
            xpath_dict[city] = 'SH_TYPE_0'
        elif html.xpath('//div[@class="listPagBox"]/dl[@id="JS_listPag"]/dd'):
            xpath_dict[city] = 'SH_TYPE_1'
        else:
            need_parse.append(city)

        time.sleep(0.1)

    print(f'Xpath Dict:{xpath_dict}')
    print(f'Need Parse:{need_parse}')
    print(f'Not Available:{not_available}')



def get_sh_available_city():
    '''
    获取当前二手房的可用城市列表
    '''
    print(SH_XPATH_DICT.keys())




if __name__ == '__main__':
    get_sh_available_city()