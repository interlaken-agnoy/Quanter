import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()
test = pd.DataFrame()
name_list = ['603613.SH',
             '002359.SZ',
             '300615.SZ',
             '600240.SH',
             '603920.SH',
             '300710.SZ',
             '002119.SZ'
             '603496.SH',
             '603136.SH',
             '300570.SZ',
             '300379.SZ',
             '300239.SZ',
             '300636.SZ',
             '603386.SH'
             ]
for ts_code in name_list:
    df = ts.pro_bar( ts_code=ts_code, start_date='20190701', end_date='201910819', ma=[20] )
    test = test.append( df.head( 1 ).ma20)

