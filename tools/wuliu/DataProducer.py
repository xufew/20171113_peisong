# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
sys.path.append('../../')

import pandas as pd

from .. import base_few
import Config


class DataProducer():
    '''
    通讯获取数据
    '''
    def __init__(self):
        self.time = 0
        self.table = base_few.DaoBase(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='hui182014734',
                db='wuliu',
                table='delivery_moniter'
                )
        self.timer = base_few.Timer()

    def count_first_time(self):
        '''
        计算首次有单时间
        '''

    def count_first_time_sql(self):
        '''
        数据库版
        '''
        minTime = self.table.run_sql(
                'select min(order_time) from `order`'
                )[0][0]
        self.time = minTime

    def produce_order(self):
        '''
        生成一分钟的订单数据
        '''

    def produce_order_sql(self):
        '''
        数据库版
        '''
        rangeTime = Config.order_time_range
        # 计算所派订单时间段
        startUnix = self.time
        startTime = self.timer.trans_unix_to_datetime(self.time)
        endTime = self.timer.add_second_datetime(startTime, rangeTime)
        endUnix = self.timer.trans_datetime_to_unix(endTime)
        print(startTime)
        print(endTime)
        # 获取订单
        orderValue = self.table.run_sql(
                'select * from `order` where order_time>= {} and order_time<{}'.format(
                    startUnix, endUnix
                    )
                )
        # 计时器替换，时间过了range分钟
        self.time = endUnix
        return orderValue

    def produce_rider(self):
        '''
        用来第一次获取全部骑士信息
        rider_id,aoi_id,mcx,mcy,max_load,min_complete,speed
        '''

    def produce_rider_sql(self, limit_num=0):
        '''
        数据库版
        rider_id,aoi_id,mcx,mcy,max_load,min_complete,speed
        '''
        countNum = self.table.run_sql('select count(rider_id) from rider')[0][0]
        if limit_num:
            outValue = self.table.run_sql(
                    'select * from rider limit {}'.format(limit_num)
                    )
        else:
            outValue = self.table.run_sql(
                    'select * from rider'
                    )
        return outValue
