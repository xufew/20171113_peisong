# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys

import numpy as np

import Config
sys.path.append(Config.base_few_path)
import base_few


def get_score_order_rider(
        orderDic, riderFrame, orderId,
        riderId, similarSet, timeNow
        ):
    '''
    计算订单和骑士之间的打分
    '''
    outScore = 0
    con1 = type(orderId) is type(1)
    con2 = type(orderId) is type(np.int)
    if con1 or con2:
        # 获取相关有用数据
        shopX = orderDic[orderId]['shopMcx']
        shopY = orderDic[orderId]['shopMcy']
        riderX = riderFrame[riderId]['mcx']
        riderY = riderFrame[riderId]['mcy']
        riderStatus = riderFrame[riderId]['status']
        desX = riderFrame[riderId]['desX']
        desY = riderFrame[riderId]['desY']
        riderFinish = riderFrame[riderId]['finishComplete']
        finishTime = riderFrame[riderId]['finishTime']
        riderSpeed = riderFrame[riderId]['speed']
        userX = orderDic[orderId]['userMcx']
        userY = orderDic[orderId]['userMcy']
        expectTime = orderDic[orderId]['expectTime']
        waitTime = orderDic[orderId]['waitSecs']
        # 公用筛选变量
        if riderStatus == 'leisure':
            riderUseX = riderX
            riderUseY = riderY
            timeUse = timeNow
        elif riderStatus == 'processing':
            riderUseX = desX
            riderUseY = desY
            timeUse = finishTime
        # 骑士离此单的开始位置比较近, 输出-1~2
        outScore += Config.score_distance*distance_near(
                shopX, shopY, riderStatus, riderUseX, riderUseY
                )
        # 骑士不够10单
        if riderFinish < 10:
            outScore += Config.score_not_ten*1
        # 骑士接了此单之后，是否可以准时完成此单, timeScore:-1~1
        exactScore, timeScore = exact_finish(
                timeUse, riderSpeed, riderUseX,
                riderUseY, userX, userY, shopX,
                shopY, expectTime, waitTime
                )
        outScore += Config.score_exact_finish*exactScore
        outScore += Config.score_time_score*timeScore
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


def distance_near(
        shopX, shopY, riderStatus, riderUseX, riderUseY
        ):
    '''
    下一单的起始位置，离本单的结束位置近
    '''
    shopRiderDis = base_few.Mercator.getDistance(
            (float(shopX), float(shopY)), (float(riderUseX), float(riderUseY))
            )
    # 开始评分
    disScore = 2-shopRiderDis/float(1000)
    if disScore < -1:
        disScore = -1
    return disScore

def exact_finish(
        timeUse, riderSpeed, riderUseX,
        riderUseY, userX, userY, shopX,
        shopY, expectTime, waitTime
        ):
    '''
    骑士可以准时送达和骑士完成所需时间
    '''
    exactScore = 0
    timeScore = 0
    timer = base_few.Timer()
    timeUse = timer.trans_unix_to_datetime(timeUse)
    expectTime = timer.trans_unix_to_datetime(expectTime)
    #
    riderToShop = base_few.Mercator.getDistance(
            (float(riderUseX), float(riderUseY)), (float(shopX), float(shopY))
            )/float(riderSpeed)
    shopToUser = base_few.Mercator.getDistance(
            (float(shopX), float(shopY)), (float(userX), float(userY))
            )/float(riderSpeed)
    atShopTime = timer.add_second_datetime(timeUse, riderToShop)
    waitShopTime = timer.add_second_datetime(timeUse, waitTime)
    # 可以完成时间
    if atShopTime >= waitShopTime:
        finishTime = timer.add_second_datetime(atShopTime, shopToUser)
    else:
        finishTime = timer.add_second_datetime(waitShopTime, shopToUser)
    if expectTime > finishTime:
        exactScore = 1
    # 完成所需时间
    if atShopTime >= waitShopTime:
        totalTime = (riderToShop+shopToUser)/60.0
    else:
        totalTime = (waitTime+shopToUser)/60.0
    timeScore = 1-totalTime/30.0
    if timeScore < -1:
        timeScore = -1
    return exactScore, timeScore
