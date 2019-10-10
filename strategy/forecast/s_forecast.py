# coding:utf-8
# Created : 2019-08-29
# updated : 2019-09-05
# Author：Ethan Wang

pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('max_colwidth', 200)  # 设置value的显示长度为100，默认为50

ts.set_token('33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668')
pro = ts.pro_api()