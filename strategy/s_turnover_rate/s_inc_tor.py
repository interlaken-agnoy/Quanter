# coding:utf-8
# Created : 2019-08-26
# updated : 2019-08-26
# Author：Ethan Wang

'''
换手率法挖掘热门股,换手率放大
'''

import datetime

import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

# 设置今天日期
today = (datetime.date.today() - datetime.timedelta( days=1 ))
yday = today - datetime.timedelta( days=3 )
dbfday = today - datetime.timedelta( days=4 )
# 转为tushare格式的时间
today = today.strftime( "%Y%m%d" )
yday = yday.strftime( "%Y%m%d" )
dbfday = dbfday.strftime( "%Y%m%d" )

turnover_rarion_bound = {"今日换手率下限": 3,
                         "今日换手率上限": 6,
                         '今日涨跌幅下限': -4,
                         '今日涨跌幅上限': 4,
                         '流通股本(亿)': 3,
                         '股价(元)': 25,
                         '市盈率(pe)上限': 100,
                         '市盈率(pe)下限': 15,
                         '昨日换手率': 3,
                         '前日换手率': 2.5}

merge_tday_basic = pd.DataFrame()
inc_turnover_rate = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name,industry,list_date' )


# 获取今日收盘数据
def get_today_basic():  # 得到今日收盘数据表
    today_basic = pro.daily_basic( ts_code='', trade_date=today,
                                   fields='ts_code, close, pe, pe_ttm, pb, float_share, turnover_rate' )

    merge_tday_basic = pd.merge( name_list, today_basic, on='ts_code', sort=False,
                                 left_index=False, right_index=False, how='left' )
    merge_tday_basic.to_excel( "merge_tday_basic.xlsx" )
    return merge_tday_basic


def get_inc_turnover_rate():  # 获取换手率依次增大的股票
    # 获取昨天的列表
    yday_basic = pro.daily_basic( ts_code='', trade_date=yday,
                                  fields='ts_code, turnover_rate' )
    merge_today_yesterday = pd.merge( merge_tday_basic, yday_basic, on='ts_code', sort=False,
                                      left_index=False, right_index=False, how='inner' )
    merge_today_yesterday.rename( columns={'turnover_rate_x': 'turnover_rate_tday',
                                           'turnover_rate_y': 'turnover_rate_yday', }, inplace=True )

    # 获取前天的列表
    dbfday_basic = pro.daily_basic( ts_code='', trade_date=dbfday,
                                    fields='ts_code, turnover_rate' )

    # merge今天  昨天 前天的列表
    merge_tday_yday_dbfday = pd.merge( merge_today_yesterday, dbfday_basic, on='ts_code', sort=False,
                                       left_index=False, right_index=False, how='inner' )
    merge_tday_yday_dbfday.rename( columns={'turnover_rate': 'turnover_rate_dbfday'}, inplace=True )

    merge_tday_yday_dbfday.to_excel( 'merge_tday_yday_dbfday.xlsx' )

    # 筛选换手率： 今天>昨天>前天

    con1 = merge_tday_yday_dbfday.turnover_rate_tday >= merge_tday_yday_dbfday.turnover_rate_yday
    con2 = merge_tday_yday_dbfday.turnover_rate_yday >= merge_tday_yday_dbfday.turnover_rate_dbfday
    con3 = merge_tday_yday_dbfday.close <= turnover_rarion_bound['股价(元)']  # 股价
    con4 = merge_tday_yday_dbfday.pe <= turnover_rarion_bound['市盈率(pe)上限']  # 市盈率上限
    con5 = merge_tday_yday_dbfday.pe > turnover_rarion_bound['市盈率(pe)下限']  # 市盈率下限
    con6 = merge_tday_yday_dbfday.turnover_rate_dbfday >= turnover_rarion_bound['前日换手率']  # 前天换手率大于1.5%
    con7 = merge_tday_yday_dbfday.turnover_rate_tday <= turnover_rarion_bound["今日换手率上限"]  # 前天换手率大于6%

    inc_turnover_rate = merge_tday_yday_dbfday[con1 & con2 & con3 & con4 & con5 & con6 & con7]
    inc_turnover_rate.to_excel( 'inc_turnover_rate' + '_'+ today +'.xlsx' )

    return merge_tday_yday_dbfday, inc_turnover_rate


if __name__ == "__main__":
    merge_tday_basic = get_today_basic()
    get_inc_turnover_rate()
