# -*- coding: utf-8 -*-
# @Time : 2019/4/1
# @Author : zxy

from collections import namedtuple

XPATH_SELECTOR = namedtuple("XpathSelector", [
    "max_page",
    "info_list",
    "house_url",
    'title',
    'name',
    'phone'
])


SH_TYPE_0 = XPATH_SELECTOR(
    max_page='//div[@class="lb_zdfy fr"]/p[@class="fl"]/span[2]/text()',
    info_list='//div[@id="qy_list_cont"]/div[@class="info_list"]',
    house_url='.//a[@class="title fl"]/@href',
    title='.//a[@class="title fl"]/text()[last()]',
    name='//div[@class="person_information"]//span[@class="p_name fl"]/text()',
    phone='//div[@class="person_info fl"]//div[@class="gr_phone_div_fr fl"]/p[1]/text()'
)

SH_TYPE_1 = XPATH_SELECTOR(
    max_page='//div[@class="triggerBox"]//p[@class="number"]/text()',
    info_list='//div[@class="listPagBox"]/dl[@id="JS_listPag"]/dd',
    house_url='./div[@class="info"]/h3[@class="name"]/a/@href',
    title='./div[@class="info"]/h3[@class="name"]/a/text()[last()]',
    name='//div[@id="personal"]//p[@class="name"]/text()',
    phone='//div[@class="telephoneBox"]/div/text()'
)

SH_TYPE_2 = XPATH_SELECTOR(
    max_page='//div[@class="pagination"]/a[last()-1]/div/text()',
    info_list='//div[@class="mainContentL fl"]//div[@class="listItem clearfix"]',
    house_url='./div[@class="listItem__info fl"]//a[@class="listItem__titleA"]/@href',
    title='./div[@class="listItem__info fl"]//a[@class="listItem__titleA"]/div/text()[last()]',
    name='//div[@class="adviser"]//div[@class="adviserName fl line1"]/a/text()',
    phone='//div[@class="adviser"]//div[@class="telBar"]/text()')

SH_XPATH_DICT = {
    'nj': SH_TYPE_0,
    'sz': SH_TYPE_1,
    'wx': SH_TYPE_0,
    'cz': SH_TYPE_1,
    'hf': SH_TYPE_0,
    'hz': SH_TYPE_1,
    'xa': SH_TYPE_1,
    'cq': SH_TYPE_0,
    'sy': SH_TYPE_1,
    'nt': SH_TYPE_0,
    'tz': SH_TYPE_1,
    'tj': SH_TYPE_1,
    'xz': SH_TYPE_1,
    'yz': SH_TYPE_1,
    'bb': SH_TYPE_0,
    'jx': SH_TYPE_0,
    'cd': SH_TYPE_1,
    'hrb': SH_TYPE_1,
    'chuzhou': SH_TYPE_1,
    'mas': SH_TYPE_1,
    'bd': SH_TYPE_0,
    'fy': SH_TYPE_1,
    'zunyi': SH_TYPE_1,
    'jr': SH_TYPE_1,
    'lz': SH_TYPE_1,
    'lyg': SH_TYPE_0,
    'la': SH_TYPE_1,
    'xx': SH_TYPE_1,
    'zj': SH_TYPE_1,
    'ty': SH_TYPE_0,
    'yc': SH_TYPE_1,
    'hy': SH_TYPE_1,
    'dy': SH_TYPE_1,
    'mianyang': SH_TYPE_0,
    'hn': SH_TYPE_1,
    'wlmq': SH_TYPE_0,
    'sh': SH_TYPE_0,
    'bh': SH_TYPE_0,
    'nc': SH_TYPE_0,
    'fcg': SH_TYPE_0,
    'aq': SH_TYPE_0,
    'tl': SH_TYPE_0,
    'xc': SH_TYPE_0,
    'wh': SH_TYPE_2
}
