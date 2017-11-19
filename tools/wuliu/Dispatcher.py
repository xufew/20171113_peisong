# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys

import numpy as np
import pandas as pd
from munkres import DISALLOWED

from .. import base_few
import Config
from .wuliu_ai import OrderRiderScore


class Dispatcher():
    '''
    进行订单的指派
    '''
    def __init__(self):
        self.groupDic = {}
        self.typeDic = {
                'riderType': 'free',             # free, processing，派给骑士的类型
                'aoiType': 'same',               # same,diff，商圈派单类型
                'minNumType': 'last',            # last,first，不够10单的骑士是否优先
                }

    def init_value(self):
        self.groupDic = {}

    def rider_similar_order(self, similarSet, dataSaver):
        '''
        未分配的订单和骑士身上挂靠的订单相似，分配给此骑士
        '''
        outList = []
        for oneSet in similarSet:
            # 判断是否存在已分配的订单
            ifHasRider = False
            for thisOrder in oneSet:
                con1 = dataSaver.orderDic[thisOrder]['processStatus'] != 'none' # 已经分配了
                if con1:
                    riderId = dataSaver.orderDic[thisOrder]['processRider']
                    ifHasRider = True
                    break
            # 将其他未分配订单给它
            if ifHasRider:
                for thisOrder in oneSet:
                    con1 = dataSaver.orderDic[thisOrder]['processStatus'] == 'none' # 未分配
                    if con1:
                        dataSaver.dispatch_order(thisOrder, riderId)
            else:
                outList.append(oneSet)
        return outList


    def rider_order_matrix(
            self, dataSaver, similarSet
            ):
        '''
        订单和骑士之间，得分矩阵计算，空闲骑士
        '''
        orderDic = dataSaver.orderDic
        riderFrame = dataSaver.riderFrame
        if self.typeDic['riderType'] == 'free':
            # 获取所有待分配订单号
            if len(orderDic) == 0:
                return False, 0
            orderFrame = pd.DataFrame(orderDic)
            orderList = list(orderFrame.columns)
            if len(orderList) == 0:
                return False, 0
            # 获取所有待分配骑士
            useFrame = pd.DataFrame(riderFrame).T
            freeRiderFrame = useFrame.loc[useFrame.loc[:, 'status'] == 'leisure', :]
            riderList = list(freeRiderFrame.index)
            if len(riderList) == 0:
                return False,0
        if self.typeDic['riderType'] == 'processing':
            # 获取所有待分配订单号
            if len(orderDic) == 0:
                return False, 0
            orderFrame = pd.DataFrame(orderDic)
            orderList = list(orderFrame.columns)
            if len(orderList) == 0:
                return False, 0
            # 获取所有待分配骑士
            useFrame = pd.DataFrame(riderFrame).T
            con1 = useFrame.status != 'leisure'
            con2 = useFrame.hasOrderNum == 0
            hasRiderFrame = useFrame.loc[con1 & con2, :]
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
        return True, outMatrixDic


    def Km_dispatch(self, orderRiderMatrix, dataSaver, munkreser):
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
            indexes = munkreser.compute(np.array(noDisMatrix))
            for thisSet in indexes:
                orderId = orderIdList[thisSet[0]]
                riderId = riderIdList[thisSet[1]]
                if type(orderId) == type(''):
                    orderList = self.groupDic[orderId]
                    dataSaver.dispatch_order(orderList, riderId)
                else:
                    dataSaver.dispatch_order(orderId, riderId)
        else:
            noDisMatrix = noDisMatrix.T
            indexes = munkreser.compute(np.array(noDisMatrix))
            for thisSet in indexes:
                orderId = orderIdList[thisSet[1]]
                riderId = riderIdList[thisSet[0]]
                if type(orderId) == type(''):
                    orderList = self.groupDic[orderId]
                    dataSaver.dispatch_order(orderList, riderId)
                else:
                    dataSaver.dispatch_order(orderId, riderId)
