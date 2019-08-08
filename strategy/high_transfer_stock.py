#coding:utf-8
#Created on 2018-07-20 
# Author：Ethan Wang
'''
选股原理
具备高送转预期的个股，具有总市值低、每股公积金高、每股收益大，流通股本少等特点
我们暂时只考虑每股公积金、每股收益、流通股本和总市值四个因素
将公积金大于等于5元，每股收益大于等于5毛，流通股本在3亿以下，总市值在100亿以内作为高送转预期目标
'''
import tushare as ts
import pandas as pd
ts.set_token('ce40c99bf1abecb931f183264ba800dfebadcd53d1bd275760f2f636')
pro = ts.pro_api()

#调用股票基本面数据和行情数据
basic = ts.get_stock_basics()
basic.to_excel("E:\Code\myshare\share\share_basic_20190601.xlsx")


hq = ts.get_today_all()
hq.to_excel("E:\Code\myshare\share\share_hp_20190601.xlsx")

'''
数据清洗整理
'''

#当前股价,如果停牌则设置当前价格为上一个交易日股价
hq['trade'] = hq.apply(lambda x:x.settlement if x.trade==0 else x.trade, axis=1)

#分别选取流通股本,总股本,每股公积金,每股收益
basedata = basic[['outstanding', 'totals', 'reservedPerShare', 'esp']]

#选取股票代码,名称,当前价格,总市值,流通市值
hqdata = hq[['code', 'name', 'trade', 'mktcap', 'nmc']]

#设置行情数据code为index列
hqdata = hqdata.set_index('code')

#合并两个数据表
data = basedata.merge(hqdata, left_index=True, right_index=True)

'''
根据上文提到的选股参数和条件，对数据进一步处理
将总市值和流通市值换成亿元单位
'''
data['mktcap'] = data['mktcap'] / 10000
data['nmc'] = data['nmc'] / 10000

#设置参数和过滤值

#每股公积金>=5
res = data.reservedPerShare >= 5
#流通股本<=3亿
out = data.outstanding <= 300000
#每股收益>=5毛
eps = data.esp >= 5
#总市值<100亿
mktcap = data.mktcap <= 100

#取并集结果：

allcrit = res & out & eps & mktcap
selected = data[allcrit]

print (selected)