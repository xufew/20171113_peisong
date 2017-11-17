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


class OrderProcesser():
    '''
    处理相似订单合并
    '''
    def __init__(self):
        pass

    def combine_order_firstime(self, orderDic, riderDic):
        similarMatrix = self.__similar_matrix(orderDic)
        similarSet = base_few.Pandas().loc_value_index(similarMatrix, 30, '>')
        # 合并为大集合
        similarSet = self.__combine_set(similarSet)
        # 对都不是未分配订单的组合进行剔除
        outList = []
        for oneSet in similarSet:
            count = 0
            for thisOrder in oneSet:
                con1 = orderDic[thisOrder]['processStatus'] != 'none'
                if con1:
                    count += 1
            if count==len(oneSet):
                continue
            else:
                outList.append(list(oneSet))
        return outList

    def __similar_matrix(self, orderDic):
        '''
        计算储存订单的相似混淆矩阵(获取的新订单)
        '''
        colnameList = list(orderDic.keys())
        colNum = len(colnameList)
        similarMatrix = pd.DataFrame(
                np.zeros((colNum, colNum)),
                columns=colnameList,
                index=colnameList
                )
        for rowIndex in range(colNum-1):
            for colIndex in range(rowIndex+1,colNum):
                thisRow = colnameList[rowIndex]
                thisCol = colnameList[colIndex]
                thisSimValue = self.cal_order_similar_once(
                        orderDic[thisRow], orderDic[thisCol]
                        )
                similarMatrix[thisRow][thisCol] = thisSimValue
                similarMatrix[thisCol][thisRow] = thisSimValue
        return similarMatrix

    def __combine_set(self, similarSet):
        '''
        计算完两两的组合之后，将包含相同相的合并为大集合
        '''
        while True:
            outList = []
            for thisDic in similarSet:
                for bigDic in outList:
                    con1 = list(thisDic)[0] in bigDic
                    con2 = list(thisDic)[1] in bigDic
                    con3 = len(bigDic)>=Config.combine_thres
                    if (con1 or con2):
                        if con3:
                            break
                        bigDic.update(thisDic)
                        break
                else:
                    outList.append(thisDic)
            if similarSet == outList:
                break
            similarSet = outList.copy()
        return outList

    def cal_order_similar_once(self, leftValue, rightValue):
        '''
        计算仅仅两个订单之间的相似度
        '''
        value = 0
        con1 = leftValue['shopMcx'] == rightValue['shopMcx']
        con2 = leftValue['shopMcy'] == rightValue['shopMcy']
        con3 = leftValue['userMcx'] == rightValue['userMcx']
        con4 = leftValue['userMcy'] == rightValue['userMcy']
        # 商户位置相同
        shopSame = con1&con2
        userSame = con3&con4
        if shopSame and userSame:
            value += 30
        elif shopSame:
            value += 15
        elif userSame:
            value += 15
        # 用户之间距离相似
        shopDisScore = 70*Config.similar_user_weight*(
                (
                    Config.similar_user_distance_thres-
                    base_few.Mercator().getDistance(
                        [leftValue['userMcx'], leftValue['userMcy']],
                        [rightValue['userMcx'], rightValue['userMcy']]
                        )
                    )/Config.similar_user_distance_thres
                )
        value += shopDisScore
        # 商户之间距离相似
        userDisScore = 70*Config.similar_shop_weight*(
                (
                    Config.similar_shop_distance_thres-
                    base_few.Mercator().getDistance(
                        [leftValue['shopMcx'], leftValue['shopMcy']],
                        [rightValue['shopMcx'], rightValue['shopMcy']]
                        )
                    )/Config.similar_shop_distance_thres
                )
        value += userDisScore
        return value
