# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
import math

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from .. import base_few
import Config
from .wuliu_ai import OrderRiderScore
from .wuliu_ai import OrderAdder


class Dispatcher():
    '''
    进行订单的指派
    '''
    def __init__(self):
        self.groupDic = {}
        self.typeDic = {
                'aoiType': 'same',               # same,diff，商圈派单类型
                'minNumType': 'last',            # last,first，不够10单的骑士是否优先
                }
        self.timer = base_few.Timer()

    def init_value(self):
        self.groupDic = {}

    def rider_order_matrix(
            self, dataSaver, similarSet
            ):
        '''
        订单和骑士之间，得分矩阵计算，空闲骑士
        '''
        orderDic = dataSaver.orderDic
        riderFrame = dataSaver.riderFrame
        # 获取所有待分配订单号
        if len(orderDic) == 0:
            return False, 0
        orderFrame = pd.DataFrame(orderDic)
        orderList = list(orderFrame.columns)
        if len(orderList) == 0:
            return False, 0
        # 获取所有待分配骑士
        useFrame = pd.DataFrame(riderFrame).T
        con2 = useFrame.hasOrderNum == 0
        hasRiderFrame = useFrame.loc[con2, :]
        riderList = list(hasRiderFrame.index)
        if len(riderList) == 0:
            return False, 0
        # 替换并单为group
        for thisList in similarSet:
            thisOrderId = thisList[0]
            self.groupDic['group_{}'.format(thisOrderId)] = thisList
            # 已有的订单id从总的里面删除
            for skipOrderId in thisList:
                orderList.remove(skipOrderId)
            orderList.append('group_{}'.format(thisOrderId))
        # 开始打分, 只接
        if self.typeDic['aoiType'] == 'diff':
            outMatrixDic = {'1':{}}
            for thisOrder in orderList:
                outMatrixDic['1'][thisOrder] = {}
                for thisRider in riderList:
                    if type(thisOrder) == type(''):
                        # 与骑士匹配的是订单组
                        thisScore = OrderRiderScore.get_score_ordergroup_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic,
                                self.groupDic
                                )
                    else:
                        thisScore = OrderRiderScore.get_score_order_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic
                                )
                    outMatrixDic['1'][thisOrder][thisRider] = thisScore
        elif self.typeDic['aoiType'] == 'same':
            outMatrixDic = {}
            for thisOrder in orderList:
                if type(thisOrder) == type(''):
                    orderAoi = orderDic[self.groupDic[thisOrder][0]]['userAoi']
                else:
                    orderAoi = orderDic[thisOrder]['userAoi']
                if orderAoi not in outMatrixDic:
                    outMatrixDic[orderAoi] = {}
                outMatrixDic[orderAoi][thisOrder] = {}
                for thisRider in riderList:
                    riderAoi = riderFrame[thisRider]['aoiId']
                    if riderAoi != orderAoi:
                        continue
                    if type(thisOrder) == type(''):
                        # 与骑士匹配的是订单组
                        thisScore = OrderRiderScore.get_score_ordergroup_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic,
                                self.groupDic
                                )
                    else:
                        # 单个订单
                        thisScore = OrderRiderScore.get_score_order_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic
                                )
                    outMatrixDic[orderAoi][thisOrder][thisRider] = thisScore
        for aoiId in outMatrixDic:
            outMatrixDic[aoiId] = pd.DataFrame(outMatrixDic[aoiId]).T
        return True, outMatrixDic


    def Km_dispatch(self, orderRiderMatrix, dataSaver, munkreser, similarSet):
        '''
        进行km分配
        '''
        orderIdList = list(orderRiderMatrix.index)
        riderIdList = list(orderRiderMatrix.columns)
        noDisMatrix = 100-orderRiderMatrix
        orderNum = noDisMatrix.shape[0]
        freeRiderNum = noDisMatrix.shape[1]
        if (orderNum==0) or (freeRiderNum==0):
            return False
        if orderNum <= freeRiderNum:
            # 转换为小的值
            row_index, col_index = linear_sum_assignment(np.array(noDisMatrix))
            indexes = [[x, y] for x,y in zip(row_index, col_index)]
            for thisSet in indexes:
                orderId = orderIdList[thisSet[0]]
                riderId = riderIdList[thisSet[1]]
                if type(orderId) == type(''):
                    orderList = self.groupDic[orderId]
                    similarSet.remove(orderList)
                    dataSaver.dispatch_order(orderList, riderId)
                else:
                    dataSaver.dispatch_order(orderId, riderId)
        else:
            noDisMatrix = noDisMatrix.T
            row_index, col_index = linear_sum_assignment(np.array(noDisMatrix))
            indexes = [[x, y] for x,y in zip(row_index, col_index)]
            for thisSet in indexes:
                orderId = orderIdList[thisSet[1]]
                riderId = riderIdList[thisSet[0]]
                if type(orderId) == type(''):
                    orderList = self.groupDic[orderId]
                    similarSet.remove(orderList)
                    dataSaver.dispatch_order(orderList, riderId)
                else:
                    dataSaver.dispatch_order(orderId, riderId)

    def dispatch_add(self, dataSaver, operRecorder):
        '''
        对正在配送的订单进行追加
        '''
        riderDic = dataSaver.riderFrame
        orderDic = dataSaver.orderDic
        nowTime = dataSaver.time
        orderList = list(dataSaver.orderDic.keys())
        for orderId in orderList:
            userNewX =  orderDic[orderId]['userMcx']
            userNewY =  orderDic[orderId]['userMcy']
            waitTime = orderDic[orderId]['waitSecs']
            orderAoi = orderDic[orderId]['userAoi']
            immediateDeliver = orderDic[orderId]['immediateDeliver']
            if not immediateDeliver:
                # 不进行预约单的插单
                continue
            for riderId in riderDic:
                ifAdd, valueDic = OrderAdder.if_add_order(
                        orderId, riderId, riderDic, orderDic, userNewX,
                        userNewY, waitTime, orderAoi, self.timer, nowTime
                        )
                if ifAdd:
                    dataSaver.rider_add_order(
                            operRecorder,
                            orderId,
                            riderId,
                            valueDic[0],
                            valueDic[1],
                            valueDic[2],
                            valueDic[3],
                            orderAoi,
                            )
                    break

    def dispatch_diff_aoi(self, dataSaver):
        '''
        派给在商圈外的骑士预约单
        '''
        removeList = []
        yuyueDic = dataSaver.yuyueDic
        riderDic = dataSaver.riderFrame
        con1 = len(yuyueDic) != 0
        if con1:
            orderList = list(yuyueDic.keys())
            for orderId in orderList:
                choosDic = {}
                orderAoi = yuyueDic[orderId]['userAoi']
                for riderId in riderDic:
                    if riderId in removeList:
                        continue
                    nowAoi = riderDic[riderId]['nowAoi']
                    riderAoi = riderDic[riderId]['aoiId']
                    con1 = nowAoi != riderAoi
                    con2 = orderAoi == riderAoi
                    if con1 and con2:
                        # 判断此骑士是否可以准时完成此单
                        expectTime = yuyueDic[orderId]['expectTime']
                        shopX = yuyueDic[orderId]['shopMcx']
                        shopY = yuyueDic[orderId]['shopMcy']
                        userX = yuyueDic[orderId]['userMcx']
                        userY = yuyueDic[orderId]['userMcy']
                        riderSpeed = riderDic[riderId]['speed']
                        con1 = riderDic[riderId]['status'] == 'leisure'
                        con2 = riderDic[riderId]['status'] == 'processing'
                        con3 = riderDic[riderId]['hasOrderNum'] == 0
                        atTime = 9999999999999999999999999999
                        if con1:
                            riderX = riderDic[riderId]['mcx']
                            riderY = riderDic[riderId]['mcy']
                            timeNow = dataSaver.time
                            atTime = self.timer.add_second_datetime(
                                    self.timer.trans_unix_to_datetime(timeNow),
                                    math.ceil(
                                        (
                                            base_few.Mercator.getDistance(
                                                [float(riderX), float(riderY)],
                                                [float(shopX), float(shopY)]
                                                )+base_few.Mercator.getDistance(
                                                    [float(shopX), float(shopY)],
                                                    [float(userX), float(userY)]
                                                    )
                                            )/float(riderSpeed)
                                        )
                                    )
                            atTime = self.timer.trans_datetime_to_unix(atTime)
                        if con2 and con3:
                            riderX = riderDic[riderId]['desX']
                            riderY = riderDic[riderId]['desY']
                            timeNow = riderDic[riderId]['finishTime']
                            atTime = self.timer.add_second_datetime(
                                    self.timer.trans_unix_to_datetime(timeNow),
                                    math.ceil(
                                        (
                                            base_few.Mercator.getDistance(
                                                [float(riderX), float(riderY)],
                                                [float(shopX), float(shopY)]
                                                )+base_few.Mercator.getDistance(
                                                    [float(shopX), float(shopY)],
                                                    [float(userX), float(userY)]
                                                    )
                                            )/float(riderSpeed)
                                        )
                                    )
                            atTime = self.timer.trans_datetime_to_unix(atTime)
                        if atTime<expectTime:
                            choosDic[riderId] = atTime
                if len(choosDic) == 0:
                    pass
                else:
                    riderId = max(choosDic, key=choosDic.get)
                    useDic = dataSaver.yuyueDic[orderId].copy()
                    dataSaver.yuyueDic.pop(orderId)
                    dataSaver.orderDic[orderId] = useDic
                    dataSaver.dispatch_order(orderId, riderId)
                    removeList.append(riderId)
                    print(orderId, riderId)
