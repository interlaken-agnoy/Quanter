#coding:utf-8
#Created on 2018-12-09 
#Author：Ethan Wang

import os
import datetime as dt
import pandas_datareader as pdr
import pandas_datareader.data as web

start = dt.datetime(2016, 1, 1)
end = dt.datetime(2017, 1, 1)

# df = pdr.get_data_yahoo('TSLA',start,end)
# print(df.head())

dict1 = {'name':'Ethan', 'Age':29, 'Title': 'Engineer'}
print(dict1)

dict1['name'] = 'Wang Renzhong'
print(dict1)

print(dict1.values())

dict3 = dict1.items()
print(dict3)

for key in dict1:
	if(dict1.get(key) == 'Wang Renzhong'):
		print('Ethan is in the list')
	else:
		print('there is no Ethan')

dict1.pop('Age')
print(dict1)


#迭代器 生成器
list1 = [10,20,'Ethan',3.1415]
print(list1)

iter1 = iter(list1)

print(next(iter1))
print(next(iter1))

for x in iter1:
	print(x)

list3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
list4 = [i+1 for i in list3]
print(list4)

'''
装饰器 2018/12/12

作用：为已经存在的对象添加额外的功能

1.Python函数可以像普通变量一样当做参数传递给另一个函数，当做其参数，可以作为返回值，可以定义在另一个函数内
'''
def use_logging(func):
	def wrapper():
		print("%s is running" % func.__name__)
		func()   # 把 foo 当做参数传递进来时，执行func()就相当于执行foo()
	return wrapper

def foo():
	print('Trump is a bitch!')


# 因为装饰器 use_logging(foo) 返回的时函数对象 wrapper，这条语句相当于  foo = wrapper
# 执行foo()就相当于执行 wrapper()

foo = use_logging(foo)
foo()

def actor():
	print('Tom Cruise is a great actor!')

actor = use_logging(actor)
actor()

@use_logging      # 语法糖， 放在函数开始的地方， 这样就可以省略最后一步赋值的操作， 等于 share = use_logging(share)
def share():
	print("Chinese share market is bullshit!")

share()



import threading
from queue import Queue
import datetime
import pandas as pd
import tushare as ts


pd.set_option( 'display.max_columns', None )  # 显示所有列
pd.set_option( 'display.max_rows', None )  # 显示所有行
pd.set_option( 'max_colwidth', 200 )  # 设置value的显示长度为100，默认为50

ts.set_token( '33c9dc31a0d5e549125e0322e6142137e2687212b171f8dde4f21668' )
pro = ts.pro_api()

# 设置时间，t为今日，t_b1为昨日
t = (datetime.date.today() - datetime.timedelta( days=1 ))
t = t.strftime( "%Y%m%d" )

name_list = pro.stock_basic( exchange='', list_status='L', fields='ts_code,name, area, industry' )

data = [range(0,500,1), range(500,1000,1), range(1000,1500,1), range(1500,2000,1)]
def s_cross_all_average(row,q):
    k_average = pd.DataFrame()
    for ts_code in name_list['ts_code'][0:500]:
        print( "正在计算穿均线策略:", ts_code )
        df = ts.pro_bar( ts_code=ts_code, adj='qfq', start_date='20170227', end_date=t, ma=[5, 10, 20, 30, 60] )[
            ['ts_code', 'close', 'low', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60']]
        k_average = k_average.append( df.head( 1 ) )  # 取第一行为今天的日均线数据
    q.put(k_average)
    print( "穿均线策略计算结束！！！" )

def multithreading():
    q = Queue()
    threads = []
    for i in range( 4 ):
        t = threading.Thread( target=s_cross_all_average, args=(data[i],q ))
        t.start()
        threads.append( t )
    for thread in threads:
        thread.join()

    results = pd.DataFrame()
    for _ in range( 4 ):
        results.append( q.get() )

    print( "穿均线策略计算结束！！！" )

if __name__ == "__main__":
    multithreading()



