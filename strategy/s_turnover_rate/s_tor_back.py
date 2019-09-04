# coding:utf-8
# Created : 2019-08-29
# updated : 2019-08-29
# Author：Ethan Wang

'''
选股策略：按当前6个交易日的换手率筛选
t (今日换手率)
t_b1
t-2
t-3(MAX)
t-4
t-5

换算率满足如下条件：
t-5<t-4<t-3
t-3>t-2>t_b1>t
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
t_b3 = t - datetime.timedelta( days=5 )
t_b4 = t - datetime.timedelta( days=6 )
t_b5 = t - datetime.timedelta( days=7 )

# t_n1为下一个交易日
t_n1 = t + datetime.timedelta( days=0 )
t_n1 = t_n1.strftime( "%Y%m%d" )

# 转为tushare格式的时间
t = t.strftime( "%Y%m%d" )
t_b1 = t_b1.strftime( "%Y%m%d" )
t_b2 = t_b2.strftime( "%Y%m%d" )
t_b3 = t_b3.strftime( "%Y%m%d" )
t_b4 = t_b4.strftime( "%Y%m%d" )
t_b5 = t_b5.strftime( "%Y%m%d" )

trade_data = [t_b1, t_b2, t_b3, t_b4, t_b5]

turnover_rarion_bound = {"今日换手率下限": 5.5,
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

merge_t_basic = pd.DataFrame()
factor_screen_selected = pd.DataFrame()
final_selected = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name,industry' )


# 获取今日收盘数据
def get_today_basic():  # 得到今日收盘数据表
    t_basic = pro.daily_basic( ts_code='', trade_date=t,
                               fields='ts_code, close,trade_date, pe, pe_ttm, pb, float_share, turnover_rate' )

    merge_t_basic = pd.merge( name_list, t_basic, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )
    merge_t_basic.rename( columns={'turnover_rate': 'turnover_rate_' + t}, inplace=True )

    # 获取下一个交易日涨幅，回测用
    t_n1_pctchg = pro.daily( ts_code='', trade_date=t_n1,  # 为了获取下一个交易日的涨幅
                             fields='ts_code, pct_chg' )
    t_n1_pctchg.rename( columns={'pct_chg': 'pct_chg_' + t_n1}, inplace=True )

    merge_t_basic = pd.merge( merge_t_basic, t_n1_pctchg, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )

    merge_t_basic.to_excel( 'merge_t_basic_' + t + '.xlsx' )

    return merge_t_basic


def get_turnover_rate_before():
    str_basic = pd.DataFrame()
    merge = pd.DataFrame()
    for str in trade_data:
        str_basic = pro.daily_basic( ts_code='', trade_date=str,
                                     fields='ts_code, turnover_rate' )
        if (str == t_b1):
            merge = pd.merge( merge_t_basic, str_basic, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='inner' )
        else:
            merge = pd.merge( merge, str_basic, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='inner' )
        merge.rename( columns={'turnover_rate': 'turnover_rate_' + str}, inplace=True )

    merge.to_excel( 'merge.xlsx' )

    return merge


def factor_screen():  # 按策略筛选换手率
    # 换手率 t<t-1<t-2<t-3
    ftor1 = merge['turnover_rate_' + t] <= merge['turnover_rate_' + t_b1]
    ftor2 = merge['turnover_rate_' + t_b1] <= merge['turnover_rate_' + t_b2]
    ftor3 = merge['turnover_rate_' + t_b2] <= merge['turnover_rate_' + t_b3]

    # 换手率 t-5<t-4<t-3
    # ftor4 = merge['turnover_rate_' + t_b5] <= merge['turnover_rate_' + t_b4]
    # ftor5 = merge['turnover_rate_' + t_b4] <= merge['turnover_rate_' + t_b3]

    # con3 = merge.close <= turnover_rarion_bound['股价(元)上限']  # 股价
    # con4 = merge.close >= turnover_rarion_bound['股价(元)下限']  # 股价
    # con5 = merge.pe <= turnover_rarion_bound['市盈率(pe)上限']  # 市盈率上限
    # con6 = merge.pe > turnover_rarion_bound['市盈率(pe)下限']  # 市盈率下限
    ftor6 = merge['turnover_rate_' + t] >= turnover_rarion_bound['今日换手率下限']  # 前天换手率小于6%
    # con8 = merge.turnover_rate_tday <= turnover_rarion_bound["今日换手率上限"]  # 前天换手率大于6%

    factor_screen_selected = merge[ftor1 & ftor2 & ftor3 & ftor6]
    factor_screen_selected.to_excel( 'factor_screen_selected_' + t + '.xlsx' )

    return factor_screen_selected


def get_ma_filter():
    ma_filter = pd.DataFrame()
    for ts_code in factor_screen_selected['ts_code']:
        print( "正在计算:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190700', end_date=t, ma=[10] )[
            ['ts_code', 'close', 'ma10']]
        ma_filter = ma_filter.append( df.head( 1 ) )  # 取第一行为今天的10日均线数据
    print( "列表factor_screen_selected循环结束！！！" )

    # 筛选运行在10日均线的股票
    fator = (ma_filter.close >= ma_filter.ma10)
    ma_filter = ma_filter[fator]

    final_selected = pd.merge( ma_filter, factor_screen_selected, on='ts_code', sort=False,
                               left_index=False, right_index=False, how='left' )
    final_selected.to_excel( 'final_selected_' + t + '.xlsx' )

    return final_selected


if __name__ == "__main__":
    merge_t_basic = get_today_basic()
    merge = get_turnover_rate_before()
    factor_screen_selected = factor_screen()
    final_selected = get_ma_filter()
