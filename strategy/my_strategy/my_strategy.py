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
import time

import pandas as pd
import tushare as ts

pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('max_colwidth', 200)  # 设置value的显示长度为100，默认为50

ts.set_token('33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668')
pro = ts.pro_api()

# 设置时间，t为今日，t_b1为昨日
t = (datetime.date.today() - datetime.timedelta(days=0))
t_b1 = t - datetime.timedelta(days=1)
t_b2 = t - datetime.timedelta(days=4)
t_b3 = t - datetime.timedelta(days=5)
t_b4 = t - datetime.timedelta(days=6)
t_b5 = t - datetime.timedelta(days=7)

# t_n1为下一个交易日
t_n1 = t + datetime.timedelta(days=1)
t_n1 = t_n1.strftime("%Y%m%d")

# 转为tushare格式的时间
t = t.strftime("%Y%m%d")
t_b1 = t_b1.strftime("%Y%m%d")
t_b2 = t_b2.strftime("%Y%m%d")
t_b3 = t_b3.strftime("%Y%m%d")
t_b4 = t_b4.strftime("%Y%m%d")
t_b5 = t_b5.strftime("%Y%m%d")

trade_data = [t_b1, t_b2, t_b3, t_b4, t_b5]

# 获取股票代码，名字
name_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name, area, industry')


# 获取今日收盘数据
def get_today_basic() :  # 得到今日收盘数据表
    t_basic = pro.daily_basic(ts_code='', trade_date=t,
                              fields='ts_code, close,trade_date, pe, pe_ttm, pb, float_share, turnover_rate_f')

    merge_t_basic = pd.merge(name_list, t_basic, on='ts_code', sort=False,
                             left_index=False, right_index=False, how='left')
    merge_t_basic.rename(columns={'turnover_rate_f' : 'turnover_rate_f_' + t}, inplace=True)

    # 获取昨日涨幅
    t_b1_pctchg = pro.daily(ts_code='', trade_date=t_b1,  # 为了获取下一个交易日的涨幅
                            fields='ts_code, pct_chg')
    t_b1_pctchg.rename(columns={'pct_chg' : 'pct_chg_' + t_b1}, inplace=True)

    merge_t_b1_basic = pd.merge(merge_t_basic, t_b1_pctchg, on='ts_code', sort=False,
                                left_index=False, right_index=False, how='left')

    # 获取今日涨幅
    t_pctchg = pro.daily(ts_code='', trade_date=t,  # 为了获取下一个交易日的涨幅
                         fields='ts_code, pct_chg')
    t_pctchg.rename(columns={'pct_chg' : 'pct_chg_' + t}, inplace=True)

    merge_t_basic = pd.merge(merge_t_b1_basic, t_pctchg, on='ts_code', sort=False,
                             left_index=False, right_index=False, how='left')

    # 获取明日涨幅，回测
    t_n1_pctchg = pro.daily(ts_code='', trade_date=t_n1,  # 为了获取下一个交易日的涨幅
                            fields='ts_code, pct_chg')
    t_n1_pctchg.rename(columns={'pct_chg' : 'pct_chg_' + t_n1}, inplace=True)

    merge_t_basic = pd.merge(merge_t_basic, t_n1_pctchg, on='ts_code', sort=False,
                             left_index=False, right_index=False, how='left')

    # merge_t_basic.to_excel('merge_t_basic_' + t + '.xlsx')

    return merge_t_basic


def get_turnover_rate_before() :
    str_basic = pd.DataFrame()
    turnover_rate_before = pd.DataFrame()
    for str in trade_data :
        str_basic = pro.daily_basic(ts_code='', trade_date=str,
                                    fields='ts_code, turnover_rate_f')
        if (str == t_b1) :
            turnover_rate_before = pd.merge(merge_t_basic, str_basic, on='ts_code', sort=False,
                                            left_index=False, right_index=False, how='inner')
        else :
            turnover_rate_before = pd.merge(turnover_rate_before, str_basic, on='ts_code', sort=False,
                                            left_index=False, right_index=False, how='inner')
        turnover_rate_before.rename(columns={'turnover_rate_f' : 'turnover_rate_f_' + str}, inplace=True)

    # turnover_rate_before.to_excel( 'turnover_rate_before.xlsx' )

    return turnover_rate_before


def get_high_low_before() :
    str_basic = pd.DataFrame()
    high_low_before = pd.DataFrame()

    today_basic = pro.daily(ts_code='', trade_date=t,
                            fields='ts_code, high, low, open, pre_close')
    today_basic.rename(columns={'high' : 'high_' + t, 'low' : 'low_' + t}, inplace=True)

    for str in trade_data :
        str_basic = pro.daily(ts_code='', trade_date=str,
                              fields='ts_code, high, low')
        if (str == t_b1) :
            high_low_before = pd.merge(today_basic, str_basic, on='ts_code', sort=False,
                                       left_index=False, right_index=False, how='inner')
        else :
            high_low_before = pd.merge(high_low_before, str_basic, on='ts_code', sort=False,
                                       left_index=False, right_index=False, how='inner')

        high_low_before.rename(columns={'high' : 'high_' + str, 'low' : 'low_' + str}, inplace=True)

    # high_low_before.to_excel( 'high_low_before.xlsx' )

    return high_low_before


def merge_tor_high_low() :
    merge = pd.merge(turnover_rate_before, high_low_before, on='ts_code', sort=False,
                     left_index=False, right_index=False, how='inner')
    # merge.to_excel( 'merge_tor_high_low_' + t + '.xlsx' )
    return merge


'''   

只根据流通股换手率筛选,前四日换手率每天均大于6%， 小于30%
 
'''


def s_pure_exchang() :
    pure_bond = {
        '市盈率(pe)上限' : 150,
        '市盈率(pe)下限' : 10,
        '市盈率(pe_ttm)下限' : 10,
        '换手率下限' : 6,
        '换手率上限' : 30,
        '股价(元)上限' : 60.0,
        '股价(元)下限' : 18.0}

    pure_ftor1 = merge['turnover_rate_f_' + t] >= pure_bond['换手率下限']
    pure_ftor2 = merge['turnover_rate_f_' + t_b1] >= pure_bond['换手率下限']
    pure_ftor3 = merge['turnover_rate_f_' + t_b2] >= pure_bond['换手率下限']
    pure_ftor4 = merge['turnover_rate_f_' + t_b3] >= pure_bond['换手率下限']

    pure_ftor5 = merge['turnover_rate_f_' + t] <= pure_bond['换手率上限']
    pure_ftor6 = merge['turnover_rate_f_' + t_b1] <= pure_bond['换手率上限']
    pure_ftor7 = merge['turnover_rate_f_' + t_b2] <= pure_bond['换手率上限']
    pure_ftor8 = merge['turnover_rate_f_' + t_b3] <= pure_bond['换手率上限']

    b_case1 = merge.pe <= pure_bond['市盈率(pe)上限']
    b_case2 = merge.pe >= pure_bond['市盈率(pe)下限']
    b_case3 = merge.pe >= pure_bond['市盈率(pe_ttm)下限']
    b_case4 = merge.close <= pure_bond['股价(元)上限']
    b_case5 = merge.close >= pure_bond['股价(元)下限']

    s_pure_exchang = merge[
        pure_ftor1 & pure_ftor2 & pure_ftor3 & pure_ftor4 & pure_ftor5 & pure_ftor6 & pure_ftor7 & pure_ftor8 &
        b_case1 & b_case2 & b_case3 & b_case4 & b_case5]

    ma_filter = pd.DataFrame()
    for ts_code in s_pure_exchang['ts_code'] :
        print("正在计算纯换手率策略:", ts_code)
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20])[
            ['ts_code', 'close', 'ma20']]
        ma_filter = ma_filter.append(df.head(1))  # 取第一行为今天的日均线数据
    print("纯换手率策略计算结束！！！")
    ma_fator1 = (ma_filter.close >= ma_filter.ma20)
    s_pure_exchang_temp = pd.merge(ma_filter, s_pure_exchang, on='ts_code', sort=False,
                                   left_index=False, right_index=False, how='left')

    s_pure_exchang_selected = s_pure_exchang_temp.copy()

    s_pure_exchang_selected.sort_values(by='pct_chg_' + t_n1, inplace=True, ascending=False)  # 重新排序
    s_pure_exchang_selected.index = range(len(s_pure_exchang_selected))

    s_pure_exchang_selected = s_pure_exchang_selected[['name', 'ts_code', 'area', 'industry', 'close_x', 'close_y',
                                                       'trade_date', 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm']]

    return s_pure_exchang_selected


'''   

只根据流通股换手率筛选
换手率 t>t_1, t-1<t-2<t-3<t-4

'''


def s_tor_factor() :
    turnover_rarion_bound = {"今日换手率下限" : 4.0,
                             "今日换手率上限" : 20,
                             '今日涨跌幅下限' : -4,
                             '今日涨跌幅上限' : 4,
                             '流通股本(亿)' : 3,
                             '股价(元)上限' : 60.0,
                             '股价(元)下限' : 5,
                             '市盈率(pe)上限' : 200,
                             '市盈率(pe)下限' : 10,
                             '市盈率(pe_ttm)下限' : 10,
                             '昨日换手率' : 3.6,
                             '前日换手率' : 6}
    # 换手率 t>t_1, t-1<t-2<t-3<t-4
    ftor1 = merge['turnover_rate_f_' + t] >= merge['turnover_rate_f_' + t_b1]
    ftor2 = merge['turnover_rate_f_' + t_b1] <= merge['turnover_rate_f_' + t_b2]
    ftor3 = merge['turnover_rate_f_' + t_b2] <= merge['turnover_rate_f_' + t_b3]
    ftor4 = merge['turnover_rate_f_' + t_b3] <= merge['turnover_rate_f_' + t_b4]
    ftor5 = merge['turnover_rate_f_' + t] >= turnover_rarion_bound['今日换手率下限']
    ftor6 = merge['turnover_rate_f_' + t_b1] >= turnover_rarion_bound["昨日换手率"]

    # 基本面
    b_case1 = merge.close <= turnover_rarion_bound['股价(元)上限']
    b_case2 = merge.close >= turnover_rarion_bound['股价(元)下限']
    b_case3 = merge.pe <= turnover_rarion_bound['市盈率(pe)上限']
    b_case4 = merge.pe >= turnover_rarion_bound['市盈率(pe)下限']
    b_case5 = merge.pe_ttm >= turnover_rarion_bound['市盈率(pe_ttm)下限']

    s_tor_factor = merge[ftor1 & ftor2 & ftor3 & ftor4 & ftor5 & ftor6 &
                         b_case1 & b_case2 & b_case3 & b_case4 & b_case5]

    ma_filter = pd.DataFrame()
    for ts_code in s_tor_factor['ts_code'] :
        print("正在计算换手率策略:", ts_code)
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20, 60])[
            ['ts_code', 'close', 'ma20', 'ma60']]
        ma_filter = ma_filter.append(df.head(1))  # 取第一行为今天的日均线数据
    print("换手率策略计算结束！！！")

    # 筛选运行在特定日均线之上的股票
    ma_fator1 = (ma_filter.close >= ma_filter.ma20)
    ma_fator2 = (ma_filter.close >= ma_filter.ma60)
    ma_filter = ma_filter[ma_fator1 & ma_fator2]

    s_tor_factor_temp = pd.merge(ma_filter, s_tor_factor, on='ts_code', sort=False,
                                 left_index=False, right_index=False, how='left')

    s_tor_factor_selected = s_tor_factor_temp.copy()

    s_tor_factor_selected.sort_values(by='pct_chg_' + t_n1, inplace=True, ascending=False)  # 重新排序
    s_tor_factor_selected.index = range(len(s_tor_factor_selected))

    s_tor_factor_selected = s_tor_factor_selected[['name', 'ts_code', 'area', 'industry', 'close_x', 'close_y',
                                                   'trade_date', 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm']]

    return s_tor_factor_selected


'''

根据收盘价格选取特定形态 V 形

'''


def s_v_style() :
    v_style_bond = {
        '今日涨跌幅下限' : -4,
        '今日涨跌幅上限' : 4,
        '流通股本(亿)' : 3,
        '市盈率(pe)上限' : 80,
        '市盈率(pe)下限' : 20,
        '市盈率(pe_ttm)下限' : 20,
        '换手率下限' : 4,
        '换手率上限' : 15,
        '股价(元)上限' : 50,
        '股价(元)下限' : 5}

    # 今日最高价>昨日最高价, 今日最低价 > 昨日最低价
    p_ftor1 = merge['high_' + t] >= merge['high_' + t_b1]
    p_ftor2 = merge['low_' + t] >= merge['low_' + t_b1]

    # 昨日最高价<前日最高价, 昨日最低价 < 前日最低价
    p_ftor3 = merge['high_' + t_b1] <= merge['high_' + t_b2]
    p_ftor4 = merge['low_' + t_b1] <= merge['low_' + t_b2]

    # 前日最高价<大前日最高价, 前日最低价 < 大前日最低价
    p_ftor5 = merge['high_' + t_b2] <= merge['high_' + t_b3]
    p_ftor6 = merge['low_' + t_b2] <= merge['low_' + t_b3]

    # 今日涨幅为正
    p_ftor7 = merge['pct_chg_' + t] < 4.0
    p_ftor8 = merge['pct_chg_' + t] > 1.5
    # 今日最低价小于昨日收盘价， 避免跳空
    p_ftor9 = merge['low_' + t] <= merge['high_' + t_b1]
    # 流通股换手率连续三天大于3%, 筛选活跃股
    p_ftor10 = merge['turnover_rate_f_' + t] >= v_style_bond['换手率下限']
    p_ftor11 = merge['turnover_rate_f_' + t_b1] >= v_style_bond['换手率下限']

    # 基本面
    b_case1 = merge.close <= v_style_bond['股价(元)上限']
    b_case2 = merge.close >= v_style_bond['股价(元)下限']
    b_case3 = merge.pe <= v_style_bond['市盈率(pe)上限']
    b_case4 = merge.pe >= v_style_bond['市盈率(pe)下限']
    b_case5 = merge.pe_ttm >= v_style_bond['市盈率(pe_ttm)下限']

    s_v_style = merge[p_ftor1 & p_ftor2 & p_ftor3 & p_ftor4 & p_ftor5 &
                      p_ftor6 & p_ftor7 & p_ftor8 & p_ftor9 & p_ftor10 & p_ftor11]

    # 加上基本面
    # s_v_style = merge[
    #     p_ftor1 & p_ftor2 & p_ftor3 & p_ftor4 & p_ftor5 & p_ftor6 &
    #     p_ftor7 & p_ftor8 & p_ftor9 & p_ftor10 & p_ftor11 &
    #     b_case1 & b_case2 & b_case3 & b_case4 & b_case5]

    ma_filter = pd.DataFrame()
    for ts_code in s_v_style['ts_code'] :
        print("正在计算V形态策略:", ts_code)
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20])[
            ['ts_code', 'close', 'ma20']]
        ma_filter = ma_filter.append(df.head(1))  # 取第一行为今天的日均线数据
    print("V形态策略计算结束！！！")

    # 筛选运行在20日均线的股票
    ma_fator = (ma_filter.close >= ma_filter.ma20)
    ma_filter = ma_filter[ma_fator]

    s_v_style_temp = pd.merge(ma_filter, s_v_style, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left')

    s_v_style_selected = s_v_style_temp.copy()
    s_v_style_selected = s_v_style_selected[['name', 'ts_code', 'area', 'industry', 'close_x', 'close_y',
                                             'trade_date', 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm']]

    s_v_style_selected.sort_values(by='pct_chg_' + t_n1, inplace=True, ascending=False)  # 重新排序
    s_v_style_selected.index = range(len(s_v_style_selected))

    # s_v_style_selected.to_excel( 's_price_factor_selected_' + t + '.xlsx' )

    return s_v_style_selected


'''
收盘十字星形态
'''


def s_doji_line() :
    doji_line_bond = {
        '十字星边界' : 0.002,
        '流通股本(亿)' : 3,
        '市盈率(pe)上限' : 200,
        '市盈率(pe)下限' : 10,
        '市盈率(pe_ttm)下限' : 10,
        '换手率下限' : 4,
        '换手率上限' : 15,
        '股价(元)上限' : 80.0,
        '股价(元)下限' : 6.0}

    doji1 = merge['open'] <= merge['close']  # 红K线
    doji2 = (abs(merge['open'] - merge['close']) / merge['open']) <= doji_line_bond['十字星边界']  # 收十字星

    # 基本面
    b_case1 = merge['turnover_rate_f_' + t] >= doji_line_bond['换手率下限']
    b_case2 = merge['turnover_rate_f_' + t_b1] >= doji_line_bond['换手率下限']
    b_case3 = merge.pe <= doji_line_bond['市盈率(pe)上限']
    b_case4 = merge.pe >= doji_line_bond['市盈率(pe)下限']
    b_case5 = merge.pe_ttm >= doji_line_bond['市盈率(pe_ttm)下限']
    b_case6 = merge.close <= doji_line_bond['股价(元)上限']
    b_case7 = merge.close >= doji_line_bond['股价(元)下限']

    s_doji = merge[doji1 & doji2 &
                   b_case1 & b_case2 & b_case3 & b_case4 & b_case5]

    # ma_filter = pd.DataFrame()
    # for ts_code in s_doji['ts_code']:
    #     print( "正在计算十字星策略:", ts_code )
    #     df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[20] )[
    #         ['ts_code', 'close', 'ma20']]
    #     ma_filter = ma_filter.append( df.head( 1 ) )  # 取第一行为今天的日均线数据
    # print( "十字星策略计算结束！！！" )
    #
    # # 筛选运行在20日均线的股票
    #
    # ma_fator = (ma_filter.close >= ma_filter.ma20)
    # ma_filter = ma_filter[ma_fator]
    #
    # s_doji_temp= pd.merge( ma_filter, s_doji, on='ts_code', sort=False,
    #                                     left_index=False, right_index=False, how='left' )

    s_doji_selected = s_doji.copy()

    s_doji_selected.sort_values(by='pct_chg_' + t_n1, inplace=True, ascending=False)  # 重新排序
    s_doji_selected.index = range(len(s_doji_selected))

    s_doji_selected = s_doji_selected[['name', 'ts_code', 'area', 'industry', 'close',
                                       'trade_date', 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe', 'pe_ttm']]

    print('十字星策略计算结束！！！')

    return s_doji_selected


'''
一根阳线穿过5，10，20，30，60日均线

'''


def s_cross_all_average() :
    cross_all_average_bond = {
        '市盈率(pe)上限' : 80,
        '市盈率(pe)下限' : 15,
        '市盈率(pe_ttm)下限' : 15,
        '换手率下限' : 4.0,
        '换手率上限' : 10.0,
        '股价(元)上限' : 40.0,
        '股价(元)下限' : 5.0}

    b_case1 = merge.close <= cross_all_average_bond['股价(元)上限']
    b_case2 = merge.close >= cross_all_average_bond['股价(元)下限']
    b_case3 = merge.pe <= cross_all_average_bond['市盈率(pe)上限']
    b_case4 = merge.pe >= cross_all_average_bond['市盈率(pe)下限']
    b_case5 = merge.pe_ttm >= cross_all_average_bond['市盈率(pe_ttm)下限']
    b_case6 = merge['turnover_rate_f_' + t] >= cross_all_average_bond['换手率下限']

    merge_temp = merge[b_case1 & b_case2 & b_case3 & b_case4 & b_case5 & b_case6]

    print(len(merge_temp))

    k_average = pd.DataFrame()
    for ts_code in merge_temp['ts_code'] :
        print("正在计算穿均线策略:", ts_code)
        df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date='20170227', end_date=t, ma=[5, 10, 20, 30, 60])[
            ['ts_code', 'close', 'low', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60']]
        k_average = k_average.append(df.head(1))  # 取第一行为今天的日均线数据
    print("穿均线策略计算结束！！！")

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

    k_average_temp = k_average[k_factor1 & k_factor2 & k_factor3 & k_factor4 & k_factor5
                               & k_factor6 & k_factor7 & k_factor8 & k_factor9 & k_factor10]

    s_cross_all_average_temp = pd.merge(k_average_temp, merge_temp, on='ts_code', sort=False,
                                        left_index=False, right_index=False, how='left')

    s_cross_all_average_selected = s_cross_all_average_temp.copy()

    s_cross_all_average_selected.sort_values(by='pct_chg_' + t_n1, inplace=True, ascending=False)  # 重新排序
    s_cross_all_average_selected.index = range(len(s_cross_all_average_selected))

    s_cross_all_average_selected = s_cross_all_average_selected[['name', 'ts_code', 'area', 'industry', 'close_x','close_y',
                                                                 'trade_date', 'pct_chg_' + t, 'pct_chg_' + t_n1, 'pe',
                                                                 'pe_ttm']]

    return s_cross_all_average_selected


if __name__ == "__main__" :
    merge_t_basic = get_today_basic()
    turnover_rate_before = get_turnover_rate_before()
    high_low_before = get_high_low_before()
    merge = merge_tor_high_low()
    s_pure_exchang_selected = s_pure_exchang()
    s_tor_factor_selected = s_tor_factor()
    s_v_style_selected = s_v_style()
    s_doji_selected = s_doji_line()
    # s_cross_all_average_selected = s_cross_all_average()
