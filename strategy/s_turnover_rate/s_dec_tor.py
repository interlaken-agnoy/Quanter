# coding:utf-8
# Created : 2019-08-29
# updated : 2019-08-29
# Author：Ethan Wang

'''
选股策略：
三天换收益率递减， 股价运行于10日线之上
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
yday = today - datetime.timedelta( days=1 )
dbfday = today - datetime.timedelta( days=2 )
nextday = today + datetime.timedelta( days=0 )
# 转为tushare格式的时间
today = today.strftime( "%Y%m%d" )
yday = yday.strftime( "%Y%m%d" )
dbfday = dbfday.strftime( "%Y%m%d" )
nextday = nextday.strftime( "%Y%m%d" )

turnover_rarion_bound = {"今日换手率下限": 3,
                         "今日换手率上限": 6,
                         '今日涨跌幅下限': -4,
                         '今日涨跌幅上限': 4,
                         '流通股本(亿)': 3,
                         '股价(元)上限': 70,
                         '股价(元)下限': 8,
                         '市盈率(pe)上限': 100,
                         '市盈率(pe)下限': 20,
                         '昨日换手率': 3,
                         '前日换手率': 6}

merge_tday_basic = pd.DataFrame()
merge_tday_yday_dbfday = pd.DataFrame()
dec_turnover_rate = pd.DataFrame()
dec_turnover_rate_ma = pd.DataFrame()
dec_turnover_rate_ma_selected = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name,industry,list_date' )


# 获取今日收盘数据
def get_today_basic():  # 得到今日收盘数据表
    today_basic = pro.daily_basic( ts_code='', trade_date=today,
                                   fields='ts_code, close,trade_date, pe, pe_ttm, pb, float_share, turnover_rate' )

    merge_tday_basic = pd.merge( name_list, today_basic, on='ts_code', sort=False,
                                 left_index=False, right_index=False, how='left' )

    # 获取下一个交易日涨幅
    nextday_pctchg = pro.daily( ts_code='', trade_date=nextday,  # 为了获取今日涨幅
                                fields='ts_code, pct_chg' )
    nextday_pctchg.rename( columns={'pct_chg': 'pct_chg_nextday'}, inplace=True )

    merge_tday_basic = pd.merge( merge_tday_basic, nextday_pctchg, on='ts_code', sort=False,
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

    con1 = merge_tday_yday_dbfday.turnover_rate_tday <= merge_tday_yday_dbfday.turnover_rate_yday
    con2 = merge_tday_yday_dbfday.turnover_rate_yday <= merge_tday_yday_dbfday.turnover_rate_dbfday
    con3 = merge_tday_yday_dbfday.close <= turnover_rarion_bound['股价(元)上限']  # 股价
    con4 = merge_tday_yday_dbfday.close >= turnover_rarion_bound['股价(元)下限']  # 股价
    con5 = merge_tday_yday_dbfday.pe <= turnover_rarion_bound['市盈率(pe)上限']  # 市盈率上限
    con6 = merge_tday_yday_dbfday.pe > turnover_rarion_bound['市盈率(pe)下限']  # 市盈率下限
    con7 = merge_tday_yday_dbfday.turnover_rate_dbfday <= turnover_rarion_bound['前日换手率']  # 前天换手率小于6%
    # con8 = merge_tday_yday_dbfday.turnover_rate_tday <= turnover_rarion_bound["今日换手率上限"]  # 前天换手率大于6%

    dec_turnover_rate = merge_tday_yday_dbfday[con1 & con2 & con3 & con4 & con5 & con6 & con7]
    dec_turnover_rate.to_excel( 'dec_turnover_rate.xlsx' )

    return merge_tday_yday_dbfday, dec_turnover_rate


def get_ma_filter():
    ma10_filter = pd.DataFrame()
    for ts_code in dec_turnover_rate['ts_code']:
        print( "正在计算:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190700', end_date=today, ma=[10] )[
            ['ts_code', 'close', 'ma10']]
        ma10_filter = ma10_filter.append( df.head( 1 ) )  #取第一行为今天的10日均线数据
    print( "列表dec_turnover_rate循环结束！！！" )
    # 筛选运行在10日均线的股票
    con1 = (ma10_filter.close >= ma10_filter.ma10)
    dec_turnover_rate_ma = ma10_filter[con1]

    dec_turnover_rate_ma_selected = pd.merge( dec_turnover_rate_ma, dec_turnover_rate, on='ts_code', sort=False,
                                              left_index=False, right_index=False, how='left' )
    dec_turnover_rate_ma_selected.to_excel( "dec_turnover_rate_ma_selected.xlsx" )

    return dec_turnover_rate_ma_selected


if __name__ == "__main__":
    merge_tday_basic = get_today_basic()
    merge_tday_yday_dbfday, dec_turnover_rate = get_inc_turnover_rate()
    dec_turnover_rate_ma_selected = get_ma_filter()
