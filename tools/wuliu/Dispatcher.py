# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
sys.path.append('../../')

import numpy as np
import pandas as pd
from munkres import DISALLOWED

from .. import base_few
import Config


class Dispatcher():
    '''
    进行订单的指派
    '''
    def __init__(self):
        self.groupDic = {}

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
            self, orderDic, riderFrame,
            similarSet, riderType, aoiType
            ):
        '''
        订单和骑士之间，得分矩阵计算，空闲骑士
        '''
        if riderType == 'free':
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
        if riderType == 'processing':
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
        for thisSet in similarSet:
            thisOrderId = thisSet[0]
            self.groupDic['group_{}'.format(thisOrderId)] = thisSet
            copyList = outMatrix.loc[thisOrderId, :]
            outMatrix.drop(index=list(thisSet), inplace=True)
            outMatrix.loc['group_{}'.format(thisOrderId)] = copyList
            # 已有的订单id从总的里面删除
            for skipOrderId in thisSet:
                orderList.remove(skipOrderId)
            orderList.append('group_{}'.format(thisOrderId))
        # 开始打分, 只接
        if aoiType == 'diff':
            outMatrixDic = {'1':{}}
            for thisOrder in orderList:
                outMatrixDic['1'][thisOrder] = {}
                for thisRider in riderList:
                    thisScore = self.__get_score_order_rider(
                            orderDic, riderFrame, thisOrder,
                            thisRider, similarSet
                            )
                    outMatrixDic['1'][thisOrder][thisRider] = thisScore
        elif aoiType == 'same':
            outMatrixDic = {}
            for thisOrder in orderList:
                orderAoi = orderDic[thisOrder]['userAoi']
                if orderAoi not in outMatrixDic:
                    outMatrixDic[orderAoi] = {}
                outMatrixDic[orderAoi][thisOrder] = {}
                for thisRider in riderList:
                    riderAoi = riderFrame[thisRider]['aoiId']
                    if riderAoi != orderAoi:
                        continue
                    thisScore = self.__get_score_order_rider(
                            orderDic, riderFrame, thisOrder,
                            thisRider, similarSet
                            )
                    outMatrixDic[orderAoi][thisOrder][thisRider] = thisScore
        return True, outMatrixDic

    def __get_score_order_rider(
            self, orderDic, riderFrame, orderId,
            riderId, similarSet
            ):
        '''
        计算订单和骑士之间的打分
        '''
        outScore = 0
        con1 = type(orderId) is type(1)
        if con1:
            # 开始进行非group的打分
            shopX = orderDic[orderId]['shopMcx']
            shopY = orderDic[orderId]['shopMcy']
            # 骑士离订单近
            if riderFrame[riderId]['status'] == 'leisure':
                riderX = riderFrame[riderId]['mcx']
                riderY = riderFrame[riderId]['mcy']
            else:
                riderX = riderFrame[riderId]['desX']
                riderY = riderFrame[riderId]['desY']
            shopRiderDis = base_few.Mercator.getDistance(
                    (float(shopX), float(shopY)), (float(riderX), float(riderY))
                    )
            if shopRiderDis < 500:
                outScore += 50
            # 骑士不够10单
            riderFinish = riderFrame[riderId]['finishComplete']
            if riderFinish < 10:
                outScore += 100
        else:
            # 开始进行group的打分
            orderList = self.groupDic[orderId]
            totalDis = 0
            for thisOrder in orderList:
                shopX = orderDic[thisOrder]['shopMcx']
                shopY = orderDic[thisOrder]['shopMcy']
                riderX = riderFrame.loc[riderId, 'mcx']
                riderY = riderFrame.loc[riderId, 'mcy']
                # 骑士距离商户距离比较近
                shopRiderDis = base_few.Mercator().getDistance((shopX, shopY), (riderX, riderY))
                totalDis += shopRiderDis
            totalDis = totalDis/float(len(orderList))
            if totalDis < 1000:
                outScore += 50
        return outScore

    def Km_dispatch(self, orderRiderMatrix, dataSaver, munkreser):
        '''
        进行km分配
        '''
        orderIdList = list(orderRiderMatrix.index)
        riderIdList = list(orderRiderMatrix.columns)
        noDisMatrix = 10000-orderRiderMatrix
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
                if type(orderId) != type(1):
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
                if type(orderId) != type(1):
                    orderList = self.groupDic[orderId]
                    dataSaver.dispatch_order(orderList, riderId)
                else:
                    dataSaver.dispatch_order(orderId, riderId)
