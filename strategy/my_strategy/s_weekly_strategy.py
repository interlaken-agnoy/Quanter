# coding:utf-8
# Created : 2020-02-10
# updated : 2020-02-10
# Author：Ethan Wang

'''
选股策略：周K上行，最高价走高
'''

import datetime
import time

import pandas as pd
import tushare as ts

pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('max_colwidth', 200)  # 设置value的显示长度为100，默认为50

ts.set_token('eddbdef67162282fc209ada482201e0378e6fdd1e2a0b0024a97db0d')
pro = ts.pro_api()

TODAY = datetime.date.today() - datetime.timedelta(days=1)
T = TODAY.strftime("%Y%m%d")

ma_filter = pd.DataFrame()
week_selected = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name, area, industry')

fun  = lambda x,y,z : x>=y>=z

#获取周线

for ts_code in name_list['ts_code'].head(3700):
    try:
        print("正在计算周线策略:", ts_code)
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', freq = 'W', start_date='20191104', end_date='20191130')[
            ['ts_code', 'close', 'open', 'high', 'low', 'pct_chg']]

        ma_filter = ma_filter.append(df.head(3))

        fun_high = fun(ma_filter[['high']].values[0], ma_filter[['high']].values[1], ma_filter[['high']].values[2])
        fun_close = fun(ma_filter[['close']].values[0], ma_filter[['close']].values[1], ma_filter[['close']].values[2])
        fun_open = fun(ma_filter[['open']].values[0], ma_filter[['open']].values[1], ma_filter[['open']].values[2])
        fun_low = fun(ma_filter[['low']].values[0], ma_filter[['low']].values[1], ma_filter[['low']].values[2])

        result = fun_high & fun_close &fun_open & fun_low

        print(result)
        if(result):
            week_selected = week_selected.append(ma_filter.head(1))

    except OSError:
        pass
    continue



