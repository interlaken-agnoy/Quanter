# encoding:utf-8
# created on 2019-02-26
# updated ：2019-08-08
# Author：Ethan Wang

import pandas as pd
import xlrd

pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

path = r'origin.xlsx'  # 设置原始数据路径

wb = xlrd.open_workbook( path )
sheets = wb.sheet_names()  # 返回所有sheet name

deposit = []  # 转存总金额
withdrawal = []  # 转取总金额

sheet_merge = pd.DataFrame()
clean_data = pd.DataFrame()

columns = ['币种', '证券名称', '成交日期', '成交价格', '成交数量', '发生金额', '资金余额', '剩余数量', '合同编号',
           '业务名称', '手续费', '印花税', '过户费', '结算费', '证券代码', '股东代码']

# 循环遍历所有sheet,合并到一张sheet
for i in range( len( sheets ) ):
    sheet = pd.read_excel( path, sheet_name=i, index=True,
                           converters={
                               "成交日期": lambda x: pd.to_datetime( x, format="%y/%m/%d", errors='coerce' ),
                               "成交数量": lambda x: pd.to_numeric( x, errors='coerce' ),
                               "发生金额": lambda x: pd.to_numeric( x, errors='coerce' )
                           } )
    sheet_merge = sheet_merge.append( sheet, sort=False )

# 数据清洗
clean_data = pd.DataFrame( sheet_merge, columns=columns )
clean_data = clean_data[~clean_data['业务名称'].str.contains( '申购配号|保证金|天添利' )]  # 删除某列包含特殊字符的行,多字符用"|"
clean_data.to_excel( "clean_data.xlsx" )

# 数据处理
row_number = clean_data.shape[0]  # 行数
columns_number = clean_data.shape[1]  # 列数

deposit = clean_data["发生金额"].groupby( clean_data['业务名称'] == "银行转存" ).sum()
withdrawal = clean_data["发生金额"].groupby( clean_data['业务名称'] == "银行转取" ).sum()



# 计算每只股票的盈利情况
grouped = clean_data["发生金额"].groupby( clean_data['证券名称'] ).sum()

share_names = grouped.index
share_values = [round( i, 2 ) for i in grouped.values]  # round函数只保留数据2位小数

profit = pd.DataFrame( {'证券名称': share_names, '盈利': share_values},
                       columns=['证券名称', '盈利'] )

profit.drop( [0], inplace=True )  # 删除第一行
profit.sort_values( by='盈利', inplace=True, ascending=False )
profit.index = range( len( profit ) )  # 重新排序

# 导出盈利列表
profit.to_excel( "profit.xlsx" )

# 输出显示
print( "转存总金额：", deposit[True])
print( "转取总金额：", withdrawal[True] )
print( "净入金金额：", deposit[True] + withdrawal[True] )
print( profit )

# 已全部清仓的股票
clearance_stocks = profit[~profit['证券名称'].str.contains( '中通国脉|长城证券|华脉科技')]
clearance_profit = clearance_stocks['盈利'].sum()
print( '已清仓盈利', clearance_profit )


