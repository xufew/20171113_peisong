# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
sys.path.append('../../')
import json

import numpy as np
import pandas as pd

from .. import base_few
import Config



class DataSaver():
    '''
    基本数据的储存和更改
    '''
    def __init__(self):
        self.riderFrame = {}
        self.orderDic = {}
        self.fenpeiDic = {}
        self.yuyueDic = {}
        self.processingDic = {}
        self.finishDic = {}
        self.time = 0
        self.timer = base_few.Timer()

    def save_rider_info(self, riderValue):
        '''
        储存骑士的基本信息
        '''
        for thisSet in riderValue:
            riderId = thisSet['rider_id']
            aoiId = thisSet['aoi_id']
            mcx = thisSet['mcx']
            mcy = thisSet['mcy']
            maxLoad = thisSet['max_load']
            minComplete = thisSet['min_complete']
            speed = thisSet['speed']
            self.riderFrame[riderId] = {
                    'riderId': riderId,
                    'aoiId': aoiId,
                    'mcx': mcx,
                    'mcy': mcy,
                    'maxLoad': maxLoad,
                    'minComplete': minComplete,
                    'speed': speed,
                    'hasLoad': 0,                       # 已取餐订单量
                    'status': 'leisure',                # 骑士状态
                    'finishComplete': 0,                # 已完成订单量
                    'desX': -1,                         # 目标地点的x坐标
                    'desY': -1,                         # 目标地点的y坐标
                    'orderList': [],                    # 骑士身上挂靠的订单list
                    'hasOrderNum': 0,
                    'processOrder': -1,                 # 正在处理的订单
                    'finishTime': -1,                   # 配送订单完成时间
                    'nowAoi': -1,                       # 现在所处商圈
                    }

    def save_order_info(self, orderSet):
        for thisSet in orderSet:
            orderId = thisSet['order_id']
            orderTime = thisSet['order_time']
            shopAoi = thisSet['shop_aoi_id']
            shopId = thisSet['shop_id']
            shopMcx = thisSet['shop_mcx']
            shopMcy = thisSet['shop_mcy']
            userAoi = thisSet['user_aoi_id']
            userId = thisSet['user_id']
            userMcx = thisSet['user_mcx']
            userMcy = thisSet['user_mcy']
            waitSecs = thisSet['wait_secs']
            immediateDeliver = thisSet['immediate_deliver']
            expectTime = thisSet['expect_time']
            if not immediateDeliver:
                thisExpectTime = self.timer.trans_unix_to_datetime(expectTime)
                thisNowTime = self.timer.trans_unix_to_datetime(self.time)
                thisRange = (thisExpectTime-thisNowTime).seconds
                if thisRange > Config.yuding_time_thres:
                    self.yuyueDic[orderId] = {
                            'orderId': orderId,
                            'orderTime': orderTime,
                            'shopAoi': shopAoi,
                            'shopId': shopId,
                            'shopMcx': shopMcx,
                            'shopMcy': shopMcy,
                            'userAoi': userAoi,
                            'userId': userId,
                            'userMcx': userMcx,
                            'userMcy': userMcy,
                            'waitSecs': waitSecs,
                            'immediateDeliver': immediateDeliver,
                            'expectTime': expectTime,
                            'processRider': -1,
                            'processStatus': 'none'
                            }
                    continue
            self.orderDic[orderId] = {
                    'orderId': orderId,
                    'orderTime': orderTime,
                    'shopAoi': shopAoi,
                    'shopId': shopId,
                    'shopMcx': shopMcx,
                    'shopMcy': shopMcy,
                    'userAoi': userAoi,
                    'userId': userId,
                    'userMcx': userMcx,
                    'userMcy': userMcy,
                    'waitSecs': waitSecs,
                    'immediateDeliver': immediateDeliver,
                    'expectTime': expectTime,
                    'processRider': -1,
                    'processStatus': 'none'
                    }


    def check_yuyue_order(self):
        '''
        用来检查是否有预约单满足时间间隔条件，可以进行分单配送
        '''
        removeList = []
        for orderId in self.yuyueDic:
            expectTime = self.timer.trans_unix_to_datetime(self.yuyueDic[orderId]['expectTime'])
            nowTime = self.timer.trans_unix_to_datetime(self.time)
            thisRange = (expectTime-nowTime).seconds
            if thisRange <= Config.yuding_time_thres:
                orderValue = self.yuyueDic[orderId].copy()
                self.orderDic[orderId] = orderValue
                removeList.append(orderId)
        for orderId in removeList:
            self.yuyueDic.pop(orderId)


    def dispatch_order(self, orderId, riderId):
        '''
        将一个订单分配到骑士的待操作列表
        '''
        con1 = type(orderId) == type([])
        if not con1:
            self.riderFrame[riderId]['orderList'].append(orderId)
            self.riderFrame[riderId]['hasOrderNum'] = len(
                    self.riderFrame[riderId]['orderList']
                    )
            self.orderDic[orderId]['processRider'] = riderId
            self.orderDic[orderId]['processStatus'] = 'fenpei'
            self.fenpeiDic[orderId] = self.orderDic[orderId].copy()
            self.orderDic.pop(orderId)
        else:
            for thisOrder in orderId:
                self.riderFrame[riderId]['orderList'].append(thisOrder)
                self.riderFrame[riderId]['hasOrderNum'] = len(
                        self.riderFrame[riderId]['orderList']
                        )
                self.orderDic[thisOrder]['processRider'] = riderId
                self.orderDic[thisOrder]['processStatus'] = 'fenpei'
                self.fenpeiDic[thisOrder] = self.orderDic[thisOrder].copy()
                self.orderDic.pop(thisOrder)

    def rider_status_from_leisure_to_processing(
            self, riderId, orderList, finishTime,
            desX, desY, desAoi
            ):
        '''
        将空闲的骑士变为配送中的骑士
        '''
        # 变动骑士指标状态
        orderNum = len(orderList)
        self.riderFrame[riderId]['status'] = 'processing'
        self.riderFrame[riderId]['processOrder'] = orderList
        self.riderFrame[riderId]['desX'] = desX
        self.riderFrame[riderId]['desY'] = desY
        self.riderFrame[riderId]['nowAoi'] = desAoi
        self.riderFrame[riderId]['orderList'] = []
        self.riderFrame[riderId]['hasOrderNum'] = 0
        self.riderFrame[riderId]['finishTime'] = finishTime
        # 变动订单位置
        for orderId in orderList:
            copyDic = self.fenpeiDic[orderId].copy()
            self.fenpeiDic.pop(orderId)
            self.processingDic[orderId] = copyDic
            self.processingDic[orderId]['processStatus'] = 'processing'

    def rider_status_finish(self, riderId, status):
        '''
        刚完成一单的骑士，进行配置
        '''
        self.riderFrame[riderId]['status'] = status
        self.riderFrame[riderId]['mcx'] = self.riderFrame[riderId]['desX']
        self.riderFrame[riderId]['mcy'] = self.riderFrame[riderId]['desY']
        finishOrderList = self.riderFrame[riderId]['processOrder']
        for finishOrderId in finishOrderList:
            self.riderFrame[riderId]['finishComplete'] += 1
            # 变动订单位置
            copyDic = self.processingDic[finishOrderId].copy()
            self.processingDic.pop(finishOrderId)
            self.finishDic[finishOrderId] = copyDic
            self.finishDic[finishOrderId]['processStatus'] = 'finish'
        if status == 'leisure':
            self.riderFrame[riderId]['processOrder'] = -1
            self.riderFrame[riderId]['desX'] = -1
            self.riderFrame[riderId]['desY'] = -1
            self.riderFrame[riderId]['finishTime'] = -1
        else:
            pass

    # def test_save(self):
    #     with open(Config.oper_info_test, 'wb') as fileWriter:
    #         fileWriter.write(
    #                 '{}\n'.format(json.dumps(self.orderDic)).encode('utf8')
    #                 )
    #         fileWriter.write(
    #                 '{}\n'.format(json.dumps(self.fenpeiDic)).encode('utf8')
    #                 )
    #         fileWriter.write(
    #                 '{}\n'.format(json.dumps(self.processingDic)).encode('utf8')
    #                 )
    #         fileWriter.write(
    #                 '{}\n'.format(json.dumps(self.finishDic)).encode('utf8')
    #                 )
    #         fileWriter.write(
    #                 '{}\n'.format(json.dumps(self.riderFrame)).encode('utf8')
    #                 )
