# coding:utf-8
# Created on 2018-07-20
# updated : 2019-08-13
# Author：Ethan Wang
'''
高送转策略
具备高送转预期的个股，具有总市值低、每股公积金高、每股收益大，流通股本少等特点
股价、每股公积金、每股收益、总股本、流通股本、总市值
将公积金大于等于5元，每股收益大于等于5毛，流通股本在3亿以下，总市值在100亿以内作为高送转预期目标
'''
import pandas as pd
import tushare as ts

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

# 设置今天日期
# today = date.today().strftime( "%Y%m%d" )

today = '20190813'

#设置参数边界
ht_bound = {'股价(元)': 25,
            '每股资本公积(元)': 2,
            '每股收益(元)': 0.5,
            '总股本(亿)': 3,
            '流通股本(亿)': 1,
            '总市值(亿)': 100}

# 股票名称列表
# 接口：stock_basic
share_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry,list_date')
share_basic.to_excel( "const_share_basic.xlsx" )

# 每日指标
# 接口：daily_basic
basic = pro.daily_basic( ts_code='', trade_date=today,
                         fields='ts_code, close, pe, pe_ttm, pb, total_share, float_share, total_mv, circ_mv, turnover_rate_f' )
basic.to_excel( "basic.xlsx" )


merge_basic =  pd.merge( share_basic, basic, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )
merge_basic.to_excel( "merge_basic.xlsx" )


# 日线行情
# 接口：daily
daily = pro.daily( ts_code='', trade_date=today,
                   fields='ts_code, close, open, high, low, pre_close' )
daily.to_excel( "daily.xlsx" )

# 合并每日基本信息
merge_basic_daily = pd.merge( merge_basic, daily, on='ts_code', sort=False,
                              left_index=False, right_index=False, how='left' )
merge_basic_daily.to_excel( 'merge_basic_daily.xlsx' )

# 财务指标数据fina_indicator
# 读取indicator.py获得的财务数据
indicators = pd.read_excel( "const_indicator.xlsx" )

'''
数据处理
'''

# 如果停牌则设置当前价格为上一个交易日股价
#merge_basic_daily['close'] = merge_basic_daily.apply( lambda x: x.pre_close if x.close == 0 else x.close, axis=1 )

# 选取股票代码,当前价格,流通股本,总股本,流通市值,总市值
ht_merge_basic_daily = merge_basic_daily[['ts_code','name', 'close_x', 'float_share', 'total_share', 'circ_mv', 'total_mv']]

# 选取股票代码,每股资本公积,每股收益
ht_indicators = indicators[['ts_code', 'capital_rese_ps', 'eps']]

# 合并两个数据表
ht_data = pd.merge( ht_merge_basic_daily, ht_indicators, left_index=False, right_index=False, on="ts_code",
                    how='inner' )


def get_high_transfer_share():
    ht_data['total_mv'] = ht_data['total_mv'] / 10000  # 根据选股参数和条件，对数据处理将总市值和流通市值换成亿元单位
    ht_data['circ_mv'] = ht_data['circ_mv'] / 10000

    ht_data['total_share'] = ht_data['total_share'] / 10000
    ht_data['float_share'] = ht_data['float_share'] / 10000

    # 设置参数和过滤值
    ht_close_x = ht_data.close_x >= ht_bound['股价(元)']  # 股价>=25

    ht_capital_rese_ps = ht_data.capital_rese_ps >= ht_bound['每股资本公积(元)']  # 每股资本公积>=5

    ht_total_share = ht_data.total_share <= ht_bound['总股本(亿)']  # 总股本<=3亿
    ht_float_share = ht_data.float_share <= ht_bound['流通股本(亿)']  # 流通股本<=1亿

    ht_eps_ps = ht_data.eps >= ht_bound['每股收益(元)']  # 每股收益>=2毛

    ht_total_mv = ht_data.total_mv <= ht_bound[ '总市值(亿)']  # 总市值<100亿

    # 取并集结果：
    ht_all_condition_meet = ht_close_x & ht_capital_rese_ps & ht_total_share & ht_float_share & ht_eps_ps & ht_total_mv
    ht_selected = ht_data[ht_all_condition_meet]

    ht_selected.index = range( len( ht_selected ) )  # 重新排序
    ht_selected.to_excel( "ht_selected.xlsx" )

if __name__ == "__main__":
    get_high_transfer_share()
