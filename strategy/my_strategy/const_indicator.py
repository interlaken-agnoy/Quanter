# coding:utf-8
# Created : 2019-08-13
# updated : 2019-08-13
# Author：Ethan Wang

'''
基本面选股
parameter：START_DATA, END_DATA,
'''
import datetime
import time

import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

today = datetime.date.today() - datetime.timedelta(days=1)
today = today.strftime( "%Y%m%d" )

# 选取财报时间段
START_DATA = '20190601'
END_DATA = '20190731'

# 获取股票代码
share_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,symbol,name,industry,list_date' )

num = len( share_list )
print( "上市公司总数：%d" % num )


# 获取上市公司财务指标数据
def get_fina_indicator():
    indicator = pd.DataFrame()
    index = int()
    for _ in range(3):
        try:
            for str in list( share_list['ts_code'] ):
                temp = pro.fina_indicator_vip( ts_code=str, start_date=START_DATA, end_date=END_DATA,
                                               fields='ts_code, eps, dt_eps, bps, roe, roe_dt, roe_yearly,  q_profit_yoy,'
                                                      'q_profit_qoq, q_netprofit_yoy, q_netprofit_qoq,'
                                                      'grossprofit_margin,q_gsprofit_margin,or_yoy, q_sales_yoy  ' )
                indicator = indicator.append( temp )
                index = index + 1
                print( '正在下载第(%d)条,%s, %s' % (index, share_list.iloc[index - 1, 0], share_list.iloc[index - 1, 2]) )
                if (index == num):
                    print( "下载完毕！！！" )
                    break
        except:
            time.sleep(2)
            print( "异常了！！！！" )

    # indicator.to_excel( 'indicator_' + today + '.xlsx' )
    return indicator


def get_daily_basic():  # 得到今日收盘数据
    basic = pro.daily_basic( ts_code='', trade_date=today,
                             fields='ts_code, close,trade_date, pe, pe_ttm, pb' )

    daily_basic = pd.merge( share_list, basic, on='ts_code', sort=False,
                            left_index=False, right_index=False, how='left' )
    # daily_basic.to_excel( 'daily_basic_' + today + '.xlsx' )

    return daily_basic


def get_merge_share():
    merge_share = pd.merge( indicator, daily_basic, on='ts_code', sort=False,
                            left_index=False, right_index=False, how='left' )
    merge_share.to_excel( 'merge_share_' + today + '.xlsx' )


if __name__ == "__main__":
    indicator = get_fina_indicator()
    daily_basic = get_daily_basic()
    merge_share = get_merge_share()
