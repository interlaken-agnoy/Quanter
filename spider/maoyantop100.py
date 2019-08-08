#coding:utf-8
#Created on 2018-12-24
# Author：Ethan Wang
import os
import requests
import re
import csv
import time

def get_one_page(url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.108 Safari/537.36'
    }
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        return response.text
    return None

#正则解析html,提取信息
def parse_one_page(html):
    pattern = r'<dd>.*?board-index.*?>(.*?)</i>.*?name.*?><a.*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?score.*?><i class="integer">(.*?)</i><i.*?fraction.*?>(.*?)</i>.*?</dd>'
    items = re.findall(pattern, html, re.S)
    return items

'''
newline = ''解决生成的csv文件不会隔行
'''

def main(offset):
    url = 'https://maoyan.com/board/4?offset='+str(offset)
    html = get_one_page(url)

with open( 'E:/Code/myshare/data2.csv', 'a', encoding='gbk', newline='' ) as csvfile:
    writer = csv.writer( csvfile )
    writer.writerow( ['Index', 'Name', 'Actor', 'Time', 'Score', 'Float'] )

        for item in parse_one_page( html ):
            writer.writerow( item )
            print(item)


for i in range(10):
    main(offset = i*10)
    time.sleep(1)
