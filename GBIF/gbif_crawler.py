from openpyxl import load_workbook
import time
import re
import os
import requests
from threading import Thread
from queue import Queue
import random

# 运行时间装饰器(计算函数运行时间)
def excute_time_decorator(func):
    def excuteTime(*args):
        start = time.time()
        func(*args)
        end = time.time()
        cost = round(end - start)
        print(f'运行时间: {cost} 秒')

    return excuteTime

class GBIFCrawler():
    def __init__(self,tier,file_name):
        self.tier = tier
        self.file_name = file_name
        self.thread_num = 5
        self.download_url = 'https://data.rbge.org.uk/search/herbarium/stitchzoom/downloadtiff.php?base={base}&tier={tier}'
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}
        self.base_queue = Queue()
        self.save_dir = 'Download'

    def get_base_list(self):
        wb = load_workbook(self.file_name)
        sheet = wb.active
        rows = list(sheet.rows)[1:]
        for row in rows:
            s = re.search(r'http://data.rbge.org.uk/herb/(.*)',row[1].value)
            base = s.group(1).strip()
            self.base_queue.put(base)

    def download(self):
        while not self.base_queue.empty():
            base = self.base_queue.get()
            print(f'正在下载图片{base}...')
            url = self.download_url.format(base=base,tier=self.tier)

            for i in range(3):
                try:
                    response = requests.get(url,headers=self.headers,stream=True)
                    if response.status_code == 200:
                        with open(f'{self.save_dir}/{base}_{self.tier}.tiff','wb') as f:
                            for chunk in response.iter_content(100000):
                                f.write(chunk)

                        print(f'图片{base}下载完成。')
                        time.sleep(random.random())
                        break

                except Exception as e:
                    print(f'请求出错,地址：{url} 错误：{e} 正在重新请求({i + 1})...')
                    time.sleep(2)

    @excute_time_decorator
    def start(self):
        print('正在获取图片编号...')
        self.get_base_list()
        print(f'图片编号获取完毕，总数：{self.base_queue.qsize()}')
        time.sleep(2)

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        print('开始下载')
        print('--------------------------------------------------------------------------')
        threads = []
        for i in range(self.thread_num):
            t = Thread(target=self.download)
            t.setDaemon(True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        print('下载完毕')


if __name__ == '__main__':
    crawler = GBIFCrawler(3,'GBIF标本网站链接.xlsx')
    crawler.start()

