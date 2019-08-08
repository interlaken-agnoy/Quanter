#coding:utf-8
#Created on 2018-12-13
#Author：Ethan Wang

import os
import requests
import re

def get_sort_list():
    response  =  requests.get('http://www.quanshuwang.com/list/1_1.html')
    response.encoding = 'gbk'
    result = response.text
    reg = r'<a target="_blank" title="(.*?)" href="(.*?)" class="clearfix stitle">'
    novel_url_list = re.findall(reg, result)
    return novel_url_list


def get_novel_url(url):
    response = requests.get(url)
    response.encoding = 'gbk'
    result = response.text
    reg = '<a href="(.*?)"  class="l mr11">'
    novel_url = re.findall(reg, result)[0]

    response = requests.get(novel_url)
    response.encoding = 'gbk'
    result = response.text
    reg = r'<li><a href="(.*?)" title=".*?">(.*?)</a></li>'
    chapter_url_list = re.findall(reg, result)
    return chapter_url_list

def get_chapter_conten(url):
    response = requests.get(url)
    response.encoding = 'gbk'
    result = response.text
    reg = r'style5\(\);</script>(.*?)<script type="text/javascript">'
    chapter_content = re.findall(reg, result, re.S)[0]   # re.S:允许正则表达式匹配多行
    return chapter_content


for novel_title, novel_url in get_sort_list():
    print(novel_title, novel_url)
    for chapter_url, chapter_title in get_novel_url(novel_url):
        chapter_content = get_chapter_conten(chapter_url)
        print('正在保存 %s' %chapter_title)
        with open('E:/Code/myshare/%s.html'%chapter_title, 'w') as fn:
            fn.write(chapter_content)


get_sort_list()