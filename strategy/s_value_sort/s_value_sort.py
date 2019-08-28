# coding:utf-8
# Created : 2019-08-25
# updated : 2019-08-25
# Author：Ethan Wang

'''
小市值策略

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

factor_bound = {"今日换手率下限": 3,
                "总市值(亿)": 20,
                "今日换手率上限": 15,
                '今日涨跌幅下限': -4,
                '今日涨跌幅上限': 4,
                '流通股本(亿)': 3,
                '股价(元)': 25,
                '市盈率(pe)上限': 60,
                '市盈率(pe)下限': 0,
                '昨日换手率': 3,
                '前日换手率': 3}

merge_tday_basic = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name,industry,list_date' )


# 获取今日收盘数据
def get_today_basic():
    today_basic = pro.daily_basic( ts_code='', trade_date=today,
                                   fields='ts_code, close, pe, pe_ttm, pb, float_share,total_mv,circ_mv, turnover_rate' )

    today_basic_pct_chg = pro.daily( ts_code='', trade_date=today,  # 为了获取今日涨幅
                                     fields='ts_code, pct_chg' )

    today_basic = pd.merge( today_basic, today_basic_pct_chg, on='ts_code', sort=False,
                            left_index=False, right_index=False, how='left' )

    # 得到今日收盘数据表
    merge_tday_basic = pd.merge( name_list, today_basic, on='ts_code', sort=False,
                                 left_index=False, right_index=False, how='left' )
    merge_tday_basic.to_excel( "merge_tday_basic.xlsx" )

    return merge_tday_basic


# 因子筛选
def get_factor_filter():
    merge_tday_basic['float_share'] = merge_tday_basic['float_share'] / 10000  # 流通股本换算成亿
    merge_tday_basic['total_mv'] = merge_tday_basic['total_mv'] / 10000  # 总市值换算成亿

    # s_tor_dn = merge_tday_basic.turnover_rate >= factor_bound["今日换手率下限"]  # 流通股换手率大于6%
    # s_tor_up = merge_tday_basic.turnover_rate <= factor_bound["今日换手率上限"]  # 流通股换手率小于20%

    # 基本面二次筛选，市盈率介于0~100
    s_float_share = merge_tday_basic.float_share <= factor_bound['流通股本(亿)']  # 流通股本
    s_total_mv = merge_tday_basic.total_mv <= factor_bound['总市值(亿)']  # 流通股本

    tor_close_up = merge_tday_basic.close <= factor_bound['股价(元)']  # 股价
    s_pe_up = merge_tday_basic.pe <= factor_bound['市盈率(pe)上限']  # 市盈率上限
    s_pe_dn = merge_tday_basic.pe > factor_bound['市盈率(pe)下限']  # 市盈率下限

    # 取今日满足所有条件股票
    factor_tday_selected = merge_tday_basic[s_float_share & s_total_mv & tor_close_up & s_pe_up & s_pe_dn]

    # 获取最终列表
    s_final_selected = factor_tday_selected.copy()
    s_final_selected.sort_values( by='total_mv', inplace=True, ascending=False )
    s_final_selected.to_excel( 's_final_selected.xlsx' )

    return s_final_selected

if __name__ == "__main__":
    merge_tday_basic = get_today_basic()
    s_final_selected = get_factor_filter()  # 小市值策略

