from spyder_tools.orequests import build_request
import json
import random
import pymongo
import re
import time


'''
CITIES = ['xm','sh']
'''

ACCOUNTS = [
    #{'username':'13002683806','password':'DdUEgONHYNIeT55vssuron31CaTEktlx1aEAxmVXy1_1apG8b3EbuFdRdtXdrEFaPDTvS0gb_pJsxKllnKImQQKRk2-cL65PIZ1SmWCrg-pCYycIqkwd8VTuVjRY2kJ9otGYycJd2D32rlKNoK_1AiX7hAh7vd8ReyEzXxwE9FY6dEwcd01P2JTNIiBGPUTNgRljX7x2YCRdV-f-AEMo4b_-rZ5ukNymDZH2Wxz1v9GW6rLYO0FpOsQiEFJ8ec0T8OXDW8lbXVJjdD2rIwxMYxfJ13QoEAtja2FShhOZS6R-syyaT4I61dMqrunBp8YtA3ZTYHgCh_M6hLe3BMy40UpntxSli5ifAoq-B2LyP6cP4UxTShsKd1chw4t8vHKDpFGCCS1Q8X-nsAQsMvZvTVoiyADHngaql-ggMRahCovXOQxZXOmEzCd8cGybI-QIwNuLlUj9dhP4Zagy2BVzfn9r_vfI6GhbhOV055DhH-jsehxBeLb-DHaekgS1CqjhAQ=='},
    #{'username':'18039868310','password':'GVdEIPvQAWghXlqzp6n1qnFiycJjLEm_ijUbaH23SAmhTdRtjk_781CtB43HIZBVCXPPJQ2Tiry4VZ3KhasK4swR9I-pjjeHrd0SpOSr7mV8lwsfdLxB6HSErDn3w97hNuDVe3M16fsmvyytD0FmdyDWjGT0yPqNZuSAOyB9gNLakjp4NpBvHPQAHXF6X7fRtbwEwat5BphIAj1MoXf40iw_w9u78g2dmNbp0nMDHaqbucp3V2k-6Dsf4r0GFuPqkAfCijDLZ97UpDzxDTTRBD5nkgoRw9Vrs7ZxsVc0oW6611sGZjiVk2YJOuYKZuJlaOUlqGhB7LdU_1Govr8RKBn98_qoIE8ELypIbEmlO2X9dDI-NR-j0t3q-_Mc9PndUFL_ktxxy0cHqqelwPEjJClcJ35Zvp-brebE3oENBxBvVt8G4PP-45IGaNyv165jhmqwGQvb53FhkqtCJknVyptmhIMLuuTYsfgubli7nDl5j4Jovyi2BTkGZEs0t9C6AQ=='},
    #{'username':'17020614467','password':'JKOd3whesPw7H3QmTS8HQX5NUGv3B4IiKuFVbNzP_KrJX97P3STMZmIiHmcRxx7WvCo6dfHaid4vUSr5Bi2fX7aOwtrVEhCQM7ZesP3Mn2wlLljsjjsOCRwOxKMa7JSkHaav_AxgHuHCWe7ql7N51qbO_u8i-Uommr50f8cb7edl9l5w6GruUZWe3H4vA9--chEOu8oYkJYkT6gb4y9sjyNKYa3XK4Fuscpu1S03IrD1zYrzV_MCTTyeQ92QuMfMM1V1ztuBZHVEr4XnH-K1yw31hlFAADXAo4nnTMQLvw8tzY5CGTHZ44kmeTbY3tTNqTeMyBWLMUJeO9j1-tSJe0ADUj2NNlsRS-I4B3d1QG2ozZf95k1nFozygnK-aRp0un2w8vg4hqQO8HFLONOv64K7U02B0DVn_6uYpLCn_XqjZV4kU8jX_kUzaeOdS3c-yiAPhfA5wDKalGmVEZEXKk_GMN1W3kXEDx1eyrBoePSXQ3ppKuPBZT_2AeKBV-q5AQ=='}
]

CITIES = ['xm','sh']

MONGO_CLIENT = 'localhost'
MONGO_DB = 'App58'
MONGO_COLLECTION = 'ZuFang'

# 保存成功数量
SAVE_SUCCEED = 0

class App58Crawler():
    # 用于获取手机号的关键参数ppu,作为类变量可在多城市爬取时,只进行一次初始化（登陆）
    # 该变量格式为[[ppu1,ppu1对应的username,ppu1的获取手机次数],[ppu2,ppu2对应的username,ppu2的获取手机次数],...]
    __ppu_username_succeed = []

    def __init__(self,city):
        self.city = city
        self.max_page = 140
        self.url = 'https://apphouse.58.com/api/list/chuzu?localname={city}&os=android&curVer=8.12.3&action=getListInfo&page={page}&params=%7B%22list_extra%22%3A%22geren%22%7D'
        self.login_url = 'https://passport.58.com/login/dologin'
        self.phone_url = 'https://houserent.m.58.com/telsecret/getPhone?infoId={info_id}&phone={username}&pageSource=detail&recomlog=&platform=app&verCode='
        self.login_data = {
            'vptype':'RSA2',
            'rsakeyversion':1,
            'source':'58app-android',
            'isremember':True,
            'validcodetype':200
        }
        self.headers = {'User-Agent':'okhttp/3.4.2'}
        self.client = pymongo.MongoClient(MONGO_CLIENT)
        self.client.admin.authenticate('root', 'csdjgs9B15BS')
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]
        self.get_phone_limit = 120
        self.delay = random.randint(2,3) + random.random()



    def login_and_get_ppu(self):
        if not self.__class__.__ppu_username_succeed:
            for account in ACCOUNTS:
                self.login_data['username'] = account['username']
                self.login_data['password'] = account['password']
                response = build_request(url=self.login_url,data=self.login_data,headers=self.headers)
                try:
                    json_info = json.loads(response.text)
                    self.__class__.__ppu_username_succeed.append([json_info['data']['ppu'],account['username'],0])
                except Exception as e:
                    print('Login Failed Error:{} username:{}'.format(e,account['username']))


    def get_page_json_info(self,page):
        url = self.url.format(city=self.city,page=page)
        response = build_request(url=url,headers=self.headers)
        try:
            json_info = json.loads(response.text)
            return json_info
        except Exception as e:
            print(f'Get Info Failed:{e} city:{self.city} page:{page}')


    def parse_and_save(self,json_info,page):
        if json_info.get('result').get('getListInfo').get('infolist'):
            info_list = json_info['result']['getListInfo']['infolist']
            for info in info_list:
                # 过滤isApartment的数据，该数据结构异常，信息不完整
                if info.get('isApartment'):
                    continue
                try:
                    info_id = info.get('infoID')
                    user_id = info.get('userID')
                    # 过滤用户已存在的数据
                    if not self.if_user_exist(info_id,user_id):
                        title = info.get('title')
                        date = self.data_clean(info.get('date'),'date') # 空 x分钟前 x小时前 mm-dd
                        price = info.get('price')
                        address = info.get('distanceDict').get('local_address')
                        phone,source_account = self.get_phone_number(info_id)

                        # 过滤没有手机号的数据
                        if not phone:
                            print(f'No phone: {info_id}')
                            continue

                        self.save_to_mongo({
                            'title':title,
                            'date':date,
                            'price':price,
                            'address':address,
                            'info_id':info_id,
                            'phone':phone,
                            'source_account': source_account,
                            'user_id':user_id,
                            'city':self.city
                        })

                        time.sleep(self.delay)


                except Exception as e:
                    print(f'Parse Info Failed:{e} city:{self.city} page:{page} infoId:{info_id}')


    def data_clean(self,data,type):
        if type == 'date':
            today = time.strftime('%Y-%m-%d')
            m = re.search(r'(\d{2}-\d{2})',data)
            if m:
                date = today[0:5] + m.group(1) if len(data) == 5 else data
            else:
                date = today

            return date


    def get_phone_number(self,info_id):
        ppu_username_succeed = random.choice(self.__class__.__ppu_username_succeed)
        ppu,username,succeed = ppu_username_succeed
        phone_headers = {
            'User-Agent':'okhttp/3.4.2',
            'ppu':ppu
        }
        phone_url = self.phone_url.format(info_id=info_id,username=username)
        response = build_request(url=phone_url,headers=phone_headers)
        phone_number = ''
        try:
            json_info = json.loads(response.text)
            if json_info.get('code') == 2 and json_info.get('message') == '系统出错啦 请稍后再试':
                print(f'{username} Exceeds The Limit.Succeed:{succeed}')
                self.__class__.__ppu_username_succeed.remove(ppu_username_succeed)
            else:
                phone_number = json_info.get('data').get('secphone')

        except Exception as e:
                print(f'Get Phone Failed Error:{e} infoID:{info_id}')

        finally:
            # 请求成功次数+1，若超出设定的最大请求限制，则从ppu列表中删除
            succeed += 1
            if succeed >= self.get_phone_limit:
                print(f'{username} Exceeds The Custom Limit.Succeed:{succeed}')
                self.__class__.__ppu_username_succeed.remove(ppu_username_succeed)
            else:
                ppu_username_succeed[2] = succeed

            return phone_number,username


    def if_user_exist(self,info_id,user_id):
        result1 = self.collection.find_one({'user_id':user_id})
        result2 = self.collection.find_one({'info_id': info_id})

        if result1 or result2:
            return True
        else:
            return False


    def save_to_mongo(self,item):
        self.collection.update_one({'phone': item['phone']}, {'$set': item}, True)
        print(f'Succed Item:{item}')
        global SAVE_SUCCEED
        SAVE_SUCCEED += 1


    def start_crawl(self):
        self.login_and_get_ppu()

        print(f'Start to crawl city:{self.city}')
        for page in range(1,self.max_page + 1):
            print(f'Crawling page:{page}')
            json_info = self.get_page_json_info(page)
            self.parse_and_save(json_info,page)
            if len(self.__class__.__ppu_username_succeed) == 0:
                print('All Accounts Exceed The Limit. Exit.')
                break

        print(f'Finished:{self.city}')


def test():
    start = time.time()

    crawler = App58Crawler('sh')
    crawler.start_crawl()

    print(f'Save Succeed:{SAVE_SUCCEED}')

    end = time.time()
    cost = round(end - start) / 60
    print(f'Execute Time: {cost} minutes')

test()



