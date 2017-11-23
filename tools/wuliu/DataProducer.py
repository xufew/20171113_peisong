# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
sys.path.append('../../')
import json

import pandas as pd

from .. import base_few
import Config


class DataProducer():
    '''
    通讯获取数据
    '''
    def __init__(self):
        self.time = 0
        self.endtime = 0
        self.changeTime = 0             # 时间转换点,从全局到商圈
        self.timer = base_few.Timer()
        self.queryer = base_few.HttpQuery(0)
        self.server = 'http://server:80'
        # self.server = 'http://192.168.108.129'

    def count_first_time(self):
        '''
        计算首次有单时间
        '''
        url = '{}/{}'.format(self.server, 'api/orders/time-range')
        result = self.queryer.send_query(url)
        self.time = result['data']['from']
        self.endtime = self.timer.trans_datetime_to_unix(
                self.timer.add_second_datetime(
                    self.timer.trans_unix_to_datetime(result['data']['to']), 120
                    )
                )

    def count_first_time_sql(self):
        '''
        数据库版
        '''
        minTime = self.table.run_sql(
                'select min(order_time) from `order`'
                )[0][0]
        self.time = minTime

    def count_data_dis(self):
        '''
        计算数据的订单出现分布，为后续同商圈，不满足10单做准备
        '''
        # 查询骑士总数
        url = '{}/{}'.format(self.server, 'api/riders/count')
        result = self.queryer.send_query(url)
        riderNum = result['data']
        riderNum = Config.change_rider_Num
        #
        startTime = self.time
        endTime = self.endtime
        url = '{}/{}'.format(self.server, 'api/orders/count')
        rangeTime = 1800
        totalValue = 0
        while True:
            thisEnd = self.timer.trans_unix_to_datetime(endTime)
            thisStart = self.timer.trans_datetime_to_unix(
                    self.timer.add_second_datetime(thisEnd, -1800)
                    )
            data = {'from': thisStart, 'to': endTime}
            value = self.queryer.send_query(url, data=data)['data']
            endTime = thisStart
            totalValue += value
            if totalValue > riderNum:
                self.changeTime = endTime
                break

    def count_order_dis(self):
        '''
        计算每个时间段订单量
        '''
        orderSer = pd.Series([])
        url = '{}/{}'.format(self.server, 'api/orders/count')
        startTime = self.time
        endTime = self.endtime
        countTime = 0
        while True:
            if countTime>endTime:
                break
            countTime = self.timer.trans_datetime_to_unix(
                    self.timer.add_second_datetime(
                        self.timer.trans_unix_to_datetime(startTime),
                        Config.order_time_count
                        )
                    )
            data = {'from': startTime, 'to': countTime}
            value = self.queryer.send_query(url, data=data)['data']
            orderSer[countTime] = value
            startTime = countTime
        return orderSer

    def produce_order(self, rangeTime=Config.order_time_range):
        '''
        生成一分钟的订单数据
        '''
        # 计算所派订单时间段
        startUnix = self.time
        startTime = self.timer.trans_unix_to_datetime(self.time)
        endTime = self.timer.add_second_datetime(startTime, rangeTime)
        endUnix = self.timer.trans_datetime_to_unix(endTime)
        print(startTime)
        print(endTime)
        # 获取订单
        getData = {
                'from': startUnix,
                'to': endUnix,
                'skip': 0,
                'size': 10000,
                }
        url = '{}/{}'.format(self.server, 'api/orders')
        orderValue = self.queryer.send_query(url, data=getData)['data']
        # 计时器替换，时间过了range分钟
        self.time = endUnix
        return orderValue

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
        url = '{}/{}'.format(self.server, 'api/riders')
        result = self.queryer.send_query(url)
        outValue = result['data']
        return outValue

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

    def post_trace(self):
        '''
        上传骑士的路径
        '''
        postList = []
        with open(Config.oper_info_path, 'rb') as fileReader:
            while True:
                stringLine = fileReader.readline().decode('utf8')
                if stringLine:
                    stringList = stringLine.strip().split('\t')
                    rider_2_id = stringList[1]
                    if len(rider_2_id) != 0:
                        postList.append(
                                {
                                    'rider_id': int(stringList[0]),
                                    'rider_2_id': int(stringList[1]),
                                    'order_id': int(stringList[2]),
                                    'mcx': stringList[3],
                                    'mcy': stringList[4],
                                    't': int(stringList[5]),
                                    'action': int(stringList[6]),
                                    }
                                )
                    else:
                        postList.append(
                                {
                                    'rider_id': int(stringList[0]),
                                    'order_id': int(stringList[2]),
                                    'mcx': stringList[3],
                                    'mcy': stringList[4],
                                    't': int(stringList[5]),
                                    'action': int(stringList[6]),
                                    }
                                )
                else:
                    break
        if len(postList) == 0:
            pass
        else:
            url = '{}/{}'.format(self.server, 'api/traces')
            result = self.queryer.post_query(url, json.dumps(postList))
