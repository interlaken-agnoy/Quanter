# coding:utf-8
# Created : 2019-08-15
# updated : 2019-08-15
# Author：Ethan Wang

'''
换手率法挖掘热门股

判断是否属于热门股的有效指标之一便是换手率,换手率高，股性趋于活跃。

1、每日收盘后对换手率进行排行，观察换手率在6%以上的个股。
2、选择流通股本数量较小的，最好在3亿以下，中小板尤佳。
3、前一日换手大于5%，量比大于2，今日涨幅大于5%，换手率大于5%
4、第二日开盘阶段量比较大排在量比排行榜前列的个股。
5、选择换手率突然放大3倍以上进入此区域或连续多日平均换手率维持在此区域的个股。
6、查看个股的历史走势中连续上涨行情发生概率较大而一日游行情发生概率较小的个股。
7、第二日开盘阶段量比较大排在量比排行榜前列的个股。
8、最好选择个人曾经操作过的、相对比较熟悉的个股进行介入操作

后市操作建议：
1、如当日涨幅超过8%且换手率维持或再次放大，大胆继续持有把握大涨行情。
2、一定要坚持持有该股3个交易日以上才能不至于错过大行情。
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

# 设置今天日期
today = (datetime.date.today() - datetime.timedelta( days=1 ))
yday = today - datetime.timedelta( days=3 )
dbfday = today - datetime.timedelta( days=4 )
# 转为tushare格式的时间
today = today.strftime( "%Y%m%d" )
yday = yday.strftime( "%Y%m%d" )
dbfday = dbfday.strftime( "%Y%m%d" )

turnover_rarion_bound = {"今日换手率下限": 3,
                         "今日换手率上限": 15,
                         '今日涨跌幅下限': -4,
                         '今日涨跌幅上限': 4,
                         '流通股本(亿)': 3,
                         '股价(元)': 25,
                         '市盈率(pe)上限': 100,
                         '市盈率(pe)下限': 0,
                         '昨日换手率': 3,
                         '前日换手率': 3}

merge_tday_basic = pd.DataFrame()
tor_tday_selected = pd.DataFrame()
tor_before_selected = pd.DataFrame()
tor_selected = pd.DataFrame()
tor_mafilter_selected = pd.DataFrame()

# 获取股票代码，名字
name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name,industry,list_date' )


# 获取今日收盘数据
def get_today_basic():
    today_basic = pro.daily_basic( ts_code='', trade_date=today,
                                   fields='ts_code, close, pe, pe_ttm, pb, float_share, turnover_rate' )

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

    tor_tor_dn = merge_tday_basic.turnover_rate >= turnover_rarion_bound["今日换手率下限"]  # 流通股换手率大于6%
    tor_tor_up = merge_tday_basic.turnover_rate <= turnover_rarion_bound["今日换手率上限"]  # 流通股换手率小于20%

    tor_pct_change_dn = merge_tday_basic.pct_chg >= turnover_rarion_bound["今日涨跌幅下限"]  # 流通股涨幅大于-4%%
    tor_pct_change_up = merge_tday_basic.pct_chg <= turnover_rarion_bound["今日涨跌幅上限"]  # 流通股涨幅大于5%%

    # 基本面二次筛选，市盈率介于0~100
    tor_float_share = merge_tday_basic.float_share <= turnover_rarion_bound['流通股本(亿)']  # 流通股本
    tor_close_up = merge_tday_basic.close <= turnover_rarion_bound['股价(元)']  # 股价
    tor_pe_up = merge_tday_basic.pe <= turnover_rarion_bound['市盈率(pe)上限']  # 市盈率上限
    tor_pe_dn = merge_tday_basic.pe > turnover_rarion_bound['市盈率(pe)下限']  # 市盈率下限

    # 取今日满足所有条件股票
    tor_tday_selected = merge_tday_basic[
        tor_tor_dn & tor_tor_up & tor_pct_change_dn & tor_pct_change_up & tor_float_share & tor_close_up & tor_pe_up & tor_pe_dn]
    tor_tday_selected.to_excel( 'tor_tday_selected.xlsx' )

    return tor_tday_selected


# 获取前两天换手率
def get_before_selected():
    # 获取昨日流通股换手率, 换手率大于5%
    yday_basic = pro.daily_basic( ts_code='', trade_date=yday,
                                  fields='ts_code, turnover_rate' )

    tor_yday = (yday_basic.turnover_rate >= turnover_rarion_bound["昨日换手率"])

    tor_yday_selected = yday_basic[tor_yday]
    tor_yday_selected.to_excel( 'tor_yday_selected.xlsx' )

    # 获取前日流通股换手率, 换手率小于3%
    dbfday_basic = pro.daily_basic( ts_code='', trade_date=dbfday,
                                    fields='ts_code, turnover_rate' )

    tor_dbfday = (dbfday_basic.turnover_rate >= turnover_rarion_bound["前日换手率"])

    tor_dbfday_selected = dbfday_basic[tor_dbfday]
    tor_dbfday_selected.to_excel( 'tor_dbfday_selected.xlsx' )

    # 合并昨天，前天筛选结果
    tor_before_selected = pd.merge( tor_yday_selected, tor_dbfday_selected, on='ts_code', sort=False,
                                    left_index=False, right_index=False, how='inner', suffixes=('_yday', '_dbfday') )
    tor_before_selected.to_excel( 'tor_before_selected.xlsx' )

    return tor_before_selected


# 最终满足条件的列表
def get_tor_selected():
    tor_selected = pd.merge( tor_tday_selected, tor_before_selected, on='ts_code', sort=False,
                             left_index=False, right_index=False, how='inner' )
    tor_selected.to_excel( 'tor_selected.xlsx' )

    return tor_selected


def get_ma_filter():
    ma_filter = pd.DataFrame()

    for ts_code in tor_selected["ts_code"]:
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20190710', end_date=today, ma=[20] )[
            ['ts_code', 'trade_date', 'close','ma20']]
        ma_filter = ma_filter.append( df.head( 1 ) )

    # 筛选收盘价大于20日均线的股票, 股价运行在布林带中轨之上
    tor_ma_filter = (ma_filter.ma20 <= ma_filter.close)

    tor_mafilter_selected = ma_filter[tor_ma_filter]
    tor_mafilter_selected.to_excel( 'tor_mafilter_selected.xlsx' )

    return tor_mafilter_selected


# 获取最终筛选列表
def get_final_selected_list():
    final_selected = pd.merge( tor_selected, tor_mafilter_selected, on='ts_code', sort=False,
                               left_index=False, right_index=False, how='inner' )
    final_selected.to_excel( 'final_selected_' + today +'.xlsx' )


if __name__ == "__main__":
    merge_tday_basic = get_today_basic()
    tor_tday_selected = get_factor_filter()
    tor_before_selected = get_before_selected()
    tor_selected = get_tor_selected()
    tor_mafilter_selected = get_ma_filter()
    get_final_selected_list()
