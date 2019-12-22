# coding:utf-8
# Created : 2019-08-29
# updated : 2019-09-05
# Author：Ethan Wang

import datetime

import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

today = datetime.date.today()
today = today.strftime( "%Y%m%d" )

START_DATA = '20190801'
END_DATE = today


# 获取今日收盘数据
def get_today_basic():
    name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name, area, industry' )
    basic = pro.daily_basic( ts_code='', trade_date=today,
                             fields='ts_code, close,trade_date, pe, pe_ttm, pb' )

    share_basic = pd.merge( name_list, basic, on='ts_code', sort=False,
                            left_index=False, right_index=False, how='left' )
    # share_basic.to_excel( 'share_basic' + today + '.xlsx' )

    return share_basic


def get_today_forecast():
    forecast = pro.forecast_vip( start_date=START_DATA, end_date=END_DATE,
                                 fields='ts_code,ann_date,end_date,type,p_change_min,p_change_max' )
    forecast_basic = pd.merge( forecast, share_basic, on='ts_code', sort=False,
                               left_index=False, right_index=False, how='left' )
    forecast_basic.to_excel( 'forecast_basic' + today + '.xlsx' )
    return forecast_basic


if __name__ == "__main__":
    share_basic = get_today_basic()
    forecast_basic = get_today_forecast()
