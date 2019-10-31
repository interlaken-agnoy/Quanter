# coding:utf-8
# Created : 2019-08-29
# updated : 2019-09-05
# Author：Ethan Wang

'''
选股策略：按当前6个交易日的换手率筛选
t (今日换手率)
t_b1
t_b2
t_b3(MAX)
t_b4
t_b5

换算率满足如下条件： 最近4个交易日换手率依次递减且今日收盘价大于10日均线
1.t-3>t-2>t_b1>t
2.今日收盘价大于ma10
3.今日换手率大于5%小于20%
4.股价介于6~100元之间
'''

import datetime

import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

# 设置时间，t为今日，t_b1为昨日
t = (datetime.date.today() - datetime.timedelta( days=0 ))
t_b1 = t - datetime.timedelta( days=1 )
t_b2 = t - datetime.timedelta( days=2 )
t_b3 = t - datetime.timedelta( days=3 )
t_b4 = t - datetime.timedelta( days=6 )
t_b5 = t - datetime.timedelta( days=7 )

# t_n1为下一个交易日
t_n1 = t + datetime.timedelta( days=1 )
t_n1 = t_n1.strftime( "%Y%m%d" )

# 转为tushare格式的时间
t = t.strftime( "%Y%m%d" )
t_b1 = t_b1.strftime( "%Y%m%d" )
t_b2 = t_b2.strftime( "%Y%m%d" )
t_b3 = t_b3.strftime( "%Y%m%d" )
t_b4 = t_b4.strftime( "%Y%m%d" )
t_b5 = t_b5.strftime( "%Y%m%d" )

trade_data = [t_b1, t_b2, t_b3]

turnover_rarion_bound = {"今日换手率下限": 4,
                         "今日换手率上限": 20,
                         '今日涨跌幅下限': -4,
                         '今日涨跌幅上限': 4,
                         '流通股本(亿)': 3,
                         '股价(元)上限': 100,
                         '股价(元)下限': 5,
                         '市盈率(pe)上限': 200,
                         '市盈率(pe)下限': 20,
                         '市盈率(pe_ttm)下限': 0,
                         '昨日换手率': 3,
                         '前日换手率': 6}

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name, area, industry' )


# 获取今日收盘数据
def get_today_basic():  # 得到今日收盘数据表
    t_basic = pro.daily_basic( ts_code='', trade_date=t,
                               fields='ts_code, close,trade_date, pe, pe_ttm, pb, float_share, turnover_rate' )

    merge_t_basic = pd.merge( name_list, t_basic, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )
    merge_t_basic.rename( columns={'turnover_rate': 'turnover_rate_' + t}, inplace=True )

    # 获取昨日涨幅
    t_b1_pctchg = pro.daily( ts_code='', trade_date=t_b1,  # 为了获取下一个交易日的涨幅
                             fields='ts_code, pct_chg' )
    t_b1_pctchg.rename( columns={'pct_chg': 'pct_chg_' + t_b1}, inplace=True )

    merge_t_b1_basic = pd.merge( merge_t_basic, t_b1_pctchg, on='ts_code', sort=False,
                                 left_index=False, right_index=False, how='left' )

    # 获取今日涨幅
    t_pctchg = pro.daily( ts_code='', trade_date=t,  # 为了获取下一个交易日的涨幅
                          fields='ts_code, pct_chg' )
    t_pctchg.rename( columns={'pct_chg': 'pct_chg_' + t}, inplace=True )

    merge_t_basic = pd.merge( merge_t_b1_basic, t_pctchg, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )

    # 获取明日涨幅，回测
    t_n1_pctchg = pro.daily( ts_code='', trade_date=t_n1,  # 为了获取下一个交易日的涨幅
                             fields='ts_code, pct_chg' )
    t_n1_pctchg.rename( columns={'pct_chg': 'pct_chg_' + t_n1}, inplace=True )

    merge_t_basic = pd.merge( merge_t_basic, t_n1_pctchg, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )

    # merge_t_basic.to_excel('merge_t_basic_' + t + '.xlsx')

    return merge_t_basic


def get_turnover_rate_before():
    str_basic = pd.DataFrame()
    turnover_rate_before = pd.DataFrame()
    for str in trade_data:
        str_basic = pro.daily_basic( ts_code='', trade_date=str,
                                     fields='ts_code, turnover_rate' )
        if (str == t_b1):
            turnover_rate_before = pd.merge( merge_t_basic, str_basic, on='ts_code', sort=False,
                                             left_index=False, right_index=False, how='inner' )
        else:
            turnover_rate_before = pd.merge( turnover_rate_before, str_basic, on='ts_code', sort=False,
                                             left_index=False, right_index=False, how='inner' )
        turnover_rate_before.rename( columns={'turnover_rate': 'turnover_rate_' + str}, inplace=True )

    # turnover_rate_before.to_excel( 'turnover_rate_before.xlsx' )

    return turnover_rate_before


def get_high_low_before():
    str_basic = pd.DataFrame()
    high_low_before = pd.DataFrame()

    today_basic = pro.daily( ts_code='', trade_date=t,
                             fields='ts_code, high, low, open, pre_close' )
    today_basic.rename( columns={'high': 'high_' + t, 'low': 'low_' + t}, inplace=True )

    for str in trade_data:
        str_basic = pro.daily( ts_code='', trade_date=str,
                               fields='ts_code, high, low' )
        if (str == t_b1):
            high_low_before = pd.merge( today_basic, str_basic, on='ts_code', sort=False,
                                        left_index=False, right_index=False, how='inner' )
        else:
            high_low_before = pd.merge( high_low_before, str_basic, on='ts_code', sort=False,
                                        left_index=False, right_index=False, how='inner' )

        high_low_before.rename( columns={'high': 'high_' + str, 'low': 'low_' + str}, inplace=True )

    # high_low_before.to_excel( 'high_low_before.xlsx' )

    return high_low_before


def merge_tor_high_low():
    merge = pd.merge( turnover_rate_before, high_low_before, on='ts_code', sort=False,
                      left_index=False, right_index=False, how='inner' )
    # merge.to_excel( 'merge_tor_high_low_' + t + '.xlsx' )
    return merge


'''

根据换手率筛选

'''


def s_tor_factor():
    # 换手率 t<t-1<t-2<t-3
    ftor1 = merge['turnover_rate_' + t] <= merge['turnover_rate_' + t_b1]
    ftor2 = merge['turnover_rate_' + t_b1] <= merge['turnover_rate_' + t_b2]
    ftor3 = merge['turnover_rate_' + t_b2] <= merge['turnover_rate_' + t_b3]

    # 换手率 t-5<t-4<t-3
    # ftor4 = merge['turnover_rate_' + t_b5] <= merge['turnover_rate_' + t_b4]
    # ftor5 = merge['turnover_rate_' + t_b4] <= merge['turnover_rate_' + t_b3]

    ftor6 = merge['turnover_rate_' + t] >= turnover_rarion_bound['今日换手率下限']
    ftor7 = merge['turnover_rate_' + t] <= turnover_rarion_bound["今日换手率上限"]

    # 基本面
    ftor8 = merge.close <= turnover_rarion_bound['股价(元)上限']
    ftor9 = merge.close >= turnover_rarion_bound['股价(元)下限']
    ftor10 = merge.pe <= turnover_rarion_bound['市盈率(pe)上限']
    ftor11 = merge.pe >= turnover_rarion_bound['市盈率(pe)下限']
    ftor12 = merge.pe_ttm >= turnover_rarion_bound['市盈率(pe_ttm)下限']

    s_tor_factor = merge[ftor1 & ftor2 & ftor3 & ftor6 & ftor7 & ftor8 & ftor9 & ftor10 & ftor11 & ftor12]

    # s_tor_factor.to_excel('s_tor_factor' + t + '.xlsx')

    ma_filter = pd.DataFrame()
    for ts_code in s_tor_factor['ts_code']:
        print( "正在计算换手率策略:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20] )[
            ['ts_code', 'close', 'ma20']]
        ma_filter = ma_filter.append( df.head( 1 ) )  # 取第一行为今天的日均线数据
    print( "换手率策略计算结束！！！" )

    # 筛选运行在特定日均线之上的股票
    ma_fator = (ma_filter.close >= ma_filter.ma20)
    ma_filter = ma_filter[ma_fator]

    s_tor_factor_selected = pd.merge( ma_filter, s_tor_factor, on='ts_code', sort=False,
                                      left_index=False, right_index=False, how='left' )

    s_tor_factor_selected = s_tor_factor_selected[
        ['ts_code', 'name', 'area', 'industry', 'close_x', 'close_y', 'open', 'pre_close', 'trade_date', 'ma20',
         'pct_chg_' + t_b1, 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm', 'pb']]

    s_tor_factor_selected.to_excel( 's_tor_factor_selected' + t + '.xlsx' )

    return s_tor_factor_selected


'''

根据收盘价格选取特定形态

'''


def s_price_factor():
    # 今日最高价>昨日最高价, 今日最低价 > 昨日最低价
    p_ftor1 = merge['high_' + t] > merge['high_' + t_b1]
    p_ftor2 = merge['low_' + t] > merge['low_' + t_b1]

    # 昨日最高价<前日最高价, 昨日最低价 < 前日最低价
    p_ftor3 = merge['high_' + t_b1] < merge['high_' + t_b2]
    p_ftor4 = merge['low_' + t_b1] < merge['low_' + t_b2]

    # 前日最高价<大前日最高价, 前日最低价 < 大前日最低价
    p_ftor5 = merge['high_' + t_b2] < merge['high_' + t_b3]
    p_ftor6 = merge['low_' + t_b2] < merge['low_' + t_b3]

    # 今日涨幅小于4%
    p_ftor7 = merge['pct_chg_' + t] < 4.0
    # 今日最低价小于昨日收盘价， 避免跳空
    p_ftor8 = merge['low_' + t] <= merge['pre_close']

    # p_ftor7 = abs(merge['pct_chg_' + t_b1]) < 1.0
    # p_ftor8 = abs(merge['pct_chg_' + t]) < 0.4
    # p_ftor9 = (abs(merge['open'] - merge['close']) /merge['open']) < 0.002

    s_price_factor = merge[p_ftor1 & p_ftor2 & p_ftor3 & p_ftor4 & p_ftor5 & p_ftor6 & p_ftor7 & p_ftor8]

    # s_price_factor.to_excel('s_price_factor' + t + '.xlsx')

    ma_filter = pd.DataFrame()
    for ts_code in s_price_factor['ts_code']:
        print( "正在计算价格形态策略:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20] )[
            ['ts_code', 'close', 'ma20']]
        ma_filter = ma_filter.append( df.head( 1 ) )  # 取第一行为今天的日均线数据
    print( "价格形态策略计算结束！！！" )

    # 筛选运行在10日均线的股票
    ma_fator = (ma_filter.close >= ma_filter.ma20)
    ma_filter = ma_filter[ma_fator]

    s_price_factor_selected = pd.merge( ma_filter, s_price_factor, on='ts_code', sort=False,
                                        left_index=False, right_index=False, how='left' )

    s_price_factor_selected = s_price_factor_selected[
        ['ts_code', 'name', 'area', 'industry', 'close_x', 'close_y', 'open', 'pre_close', 'trade_date', 'ma20',
         'pct_chg_' + t_b1, 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm', 'pb']]

    s_price_factor_selected.to_excel( 's_price_factor_selected' + t + '.xlsx' )

    return s_price_factor_selected


'''
一根阳线穿过5，10，20，30，60日均线

'''


def s_cross_all_average():
    k_average = pd.DataFrame()
    for ts_code in merge['ts_code'].head( len(merge) ):
        print( "正在计算穿均线策略:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20170227', end_date=t, ma=[5, 10, 20, 30, 60] )[
            ['ts_code', 'close', 'low', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60']]
        k_average = k_average.append( df.head( 1 ) )  # 取第一行为今天的日均线数据
    print( "穿均线策略计算结束！！！" )

    k_factor1 = k_average['close'] > k_average['ma5']
    k_factor2 = k_average['close'] > k_average['ma10']
    k_factor3 = k_average['close'] > k_average['ma20']
    k_factor4 = k_average['close'] > k_average['ma30']
    k_factor5 = k_average['close'] > k_average['ma60']

    k_factor6 = k_average['low'] < k_average['ma5']
    k_factor7 = k_average['low'] < k_average['ma10']
    k_factor8 = k_average['low'] < k_average['ma20']
    k_factor9 = k_average['low'] < k_average['ma30']
    k_factor10 = k_average['low'] < k_average['ma60']

    k_average_selected = k_average[k_factor1 & k_factor2 & k_factor3 & k_factor4 & k_factor5
                                   & k_factor6 & k_factor7 & k_factor8 & k_factor9 & k_factor10]

    s_cross_all_average_selected = pd.merge( k_average_selected, merge_t_basic, on='ts_code', sort=False,
                                             left_index=False, right_index=False, how='left' )

    s_cross_all_average_selected.to_excel( 's_cross_all_average_selected' + t + '.xlsx' )  # 满足一阳穿均线的条件
    return s_cross_all_average_selected


if __name__ == "__main__":
    merge_t_basic = get_today_basic()
    turnover_rate_before = get_turnover_rate_before()
    high_low_before = get_high_low_before()
    merge = merge_tor_high_low()
    s_tor_factor_selected = s_tor_factor()
    s_price_factor_selected = s_price_factor()
    s_cross_all_average_selected = s_cross_all_average()
