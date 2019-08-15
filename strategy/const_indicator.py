# coding:utf-8
# Created : 2019-08-13
# updated : 2019-08-13
# Author：Ethan Wang

'''
若已经运行并生成indicator.xlsx，则不需要再次运行
此文件仅在上市公司更新财报时才需要运行，更新indicator.xlsx
parameter：START_DATA, END_DATA,
'''
import time

import pandas as pd
import tushare as ts

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

# 选取财报时间段
START_DATA = '20190301'
END_DATA = '20190430'

indicator = pd.DataFrame()
index = int()

# 获取股票代码
share_basic = pro.stock_basic( exchange='', list_status='L', fields='ts_code,symbol,name,industry,list_date' )

num = len( share_basic )
print( "上市公司总数：%d" % num )
# 获取上市公司财务指标数据
for _ in range( 3 ):
    try:
        for str in list( share_basic['ts_code'] ):
            test = pro.fina_indicator_vip( ts_code=str, start_date=START_DATA, end_date=END_DATA,
                                           fields='ts_code, eps, dt_eps, bps, roe, roe_waa, roe_dt, capital_rese_ps,'
                                                  'undist_profit_ps, ann_date, end_date' )
            indicator = indicator.append( test )
            index = index + 1
            print( '正在下载第(%d)条,%s, %s' % (index, share_basic.iloc[index - 1, 0], share_basic.iloc[index - 1, 2]) )
            if (index == num):
                print( "下载完毕！！！" )
                break
    except:
        time.sleep( 2 )
        print( "异常了！！！！" )

indicator.to_excel( "const_indicator.xlsx" )
