# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
sys.path.append('../../')

import numpy as np
import pandas as pd

from .. import base_few
import Config
from .wuliu_ai import OrderSimilar


class OrderProcesser():
    '''
    处理相似订单合并
    '''
    def __init__(self):
        pass

    def combine_order(self, dataSaver):
        '''
        进行相似订单的合并
        '''
        similarList = [[]]
        orderDic = dataSaver.orderDic
        riderDic = dataSaver.riderFrame
        nowTime = dataSaver.time
        # 计算相似度矩阵
        similarMatrix = self.similar_matrix(orderDic, dataSaver)
        # 计算并单
        orderList = list(orderDic.keys())
        for orderId in orderList:
            jumpId = False
            for thisGroup in similarList:
                if jumpId:
                    break
                for compareId in thisGroup:
                    score = similarMatrix[compareId][orderId]
                    if score >= Config.combine_score_thres:
                        if len(thisGroup) < Config.combine_thres:
                            thisGroup.append(orderId)
                            jumpId = True
                            break
            if not jumpId:
                similarList.append([orderId])
        # 选出有组合的list
        outList = []
        for orderSet in similarList:
            if len(orderSet) > 1:
                outList.append(orderSet)
        return outList

    def similar_matrix(self, orderDic, dataSaver):
        '''
        相似度矩阵
        '''
        similarDic = {}
        orderList = list(orderDic.keys())
        orderNum = len(orderList)
        for i in range(orderNum-1):
            if orderList[i] not in similarDic:
                similarDic[orderList[i]] = {}
            for j in range(i+1, orderNum):
                scoreValue = OrderSimilar.cal_order_similar(
                        orderDic[orderList[i]],
                        orderDic[orderList[j]],
                        dataSaver
                        )
                similarDic[orderList[i]][orderList[j]] = scoreValue
                if orderList[j] not in similarDic:
                    similarDic[orderList[j]] = {}
                similarDic[orderList[j]][orderList[i]] = scoreValue
        return similarDic
