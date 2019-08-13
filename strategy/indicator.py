# coding:utf-8
# Created : 2019-08-13
# updated : 2019-08-13
# Author：Ethan Wang

'''
若已经运行并生成indicator.xlsx，则不需要再次运行
此文件仅在上市公司更新财报时才需要运行，更新indicator.xlsx
parameter：START_DATA, END_DATA,
today设置为前一天
'''
import time

import pandas as pd
import tushare as ts

ts.set_token( '35b181fd609f03009de99d5cb8ba6ac391ce96e2dc8b31c506c33ddb' )
pro = ts.pro_api()

# 设置今天日期
# today = date.today().strftime( "%Y%m%d" )
today = '20190812'

# 选取财报时间段
START_DATA = '20190301'
END_DATA = '20190430'

indicator = pd.DataFrame()
index = int()

# 获取股票代码
basic = pro.daily_basic( ts_code='', trade_date=today, fields='ts_code' )

for str in list( basic['ts_code'] ):
    test = pro.fina_indicator( ts_code=str, start_date=START_DATA, end_date=END_DATA,
                               fields='ts_code, eps, dt_eps, bps, roe, roe_waa, roe_dt, capital_rese_ps,'
                                      'undist_profit_ps, ann_date, end_date' )
    indicator = indicator.append( test )
    index = index + 1
    print( index )
    if (index % 80 == 0):
        time.sleep( 30 )

indicator.to_excel( "const_indicator.xlsx" )
