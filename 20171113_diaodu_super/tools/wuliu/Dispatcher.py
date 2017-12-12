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
                    con1 = thisRider in dataSaver.superDic
                    if con1:
                        if dataSaver.time < dataSaver.superDic[thisRider]['atShopTime']:
                            continue
                    if type(thisOrder) == type(''):
                        # 与骑士匹配的是订单组
                        thisScore = OrderRiderScore.get_score_ordergroup_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic,
                                self.groupDic, dataSaver
                                )
                    else:
                        thisScore = OrderRiderScore.get_score_order_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time,
                                self.typeDic, dataSaver
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
                    # 是否为超级骑士
                    ifChaoji = False
                    con1 = thisRider in dataSaver.superDic
                    if con1:
                        if dataSaver.time < dataSaver.superDic[thisRider]['atShopTime']:
                            continue
                        else:
                            ifChaoji = True
                    # 判断是否为同商圈
                    riderAoi = riderFrame[thisRider]['aoiId']
                    con1 = riderAoi != orderAoi
                    if con1:
                        if not ifChaoji:
                            continue
                    if type(thisOrder) == type(''):
                        # 与骑士匹配的是订单组
                        thisScore = OrderRiderScore.get_score_ordergroup_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time, self.typeDic,
                                self.groupDic, dataSaver
                                )
                    else:
                        # 单个订单
                        thisScore = OrderRiderScore.get_score_order_rider(
                                orderDic, riderFrame, thisOrder,
                                thisRider, similarSet, dataSaver.time,
                                self.typeDic, dataSaver
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
