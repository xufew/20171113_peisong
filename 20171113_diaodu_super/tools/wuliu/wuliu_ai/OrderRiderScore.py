# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
import math

import numpy as np

import Config
sys.path.append(Config.base_few_path)
import base_few


def get_score_ordergroup_rider(
        orderDic, riderFrame, groupName,
        riderId, similarSet, timeNow, typeDic,
        groupDic, dataSaver
        ):
    '''
    订单组和骑士之间的打分
    '''
    orderList = groupDic[groupName]
    totalScore = 0
    totalNum = len(orderList)
    for orderId in orderList:
        thisScore = get_score_order_rider(
                orderDic, riderFrame, orderId,
                riderId, similarSet, timeNow, typeDic,
                dataSaver
                )
        totalScore += thisScore
    outScore = totalScore/float(totalNum)
    return outScore


def get_score_order_rider(
        orderDic, riderFrame, orderId,
        riderId, similarSet, timeNow,
        typeDic, dataSaver
        ):
    '''
    计算订单和骑士之间的打分
    '''
    timer = base_few.Timer()
    outScore = 0
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
    userAoi = orderDic[orderId]['userAoi']
    orderTime = orderDic[orderId]['orderTime']
    nowAoi = riderFrame[riderId]['nowAoi']
    riderAoi = riderFrame[riderId]['aoiId']
    # 公用筛选变量
    if riderStatus == 'leisure':
        riderUseX = riderX
        riderUseY = riderY
        timeUse = timeNow
        outScore += Config.score_free
    elif riderStatus == 'processing':
        riderUseX = desX
        riderUseY = desY
        timeUse = finishTime
    # 骑士离此单的开始位置比较近, 输出-1~2
    outScore += Config.score_distance*distance_near(
            shopX, shopY, riderStatus, riderUseX, riderUseY
            )
    # 骑士接了此单之后，是否可以准时完成此单, timeScore:-1~1
    exactScore, timeScore = exact_finish(
            timeUse, riderSpeed, riderUseX,
            riderUseY, userX, userY, shopX,
            shopY, expectTime, waitTime, timer,
            timeNow, orderTime
            )
    outScore += Config.score_exact_finish*exactScore
    outScore += Config.score_time_score*timeScore
    # 最后满足条件特定
    if typeDic['minNumType'] == 'first':
        # 骑士不够10单
        if riderFinish < 10:
            outScore += Config.score_not_ten*1
    else:
        if riderFinish < 10:
            outScore += Config.score_not_ten_small*1
    # 订单期望时间与当前时间差(-1,1)
    if expectTime > timeNow:
        deltaTime = 1-(
                timer.trans_unix_to_datetime(expectTime)-
                timer.trans_unix_to_datetime(timeNow)
                ).seconds/float(60)/40
        if deltaTime < 0:
            deltaTime = 0
        outScore += Config.score_order_time*deltaTime
    # 骑士商圈和所在位置不符, 区分超级骑士
    if typeDic['aoiType'] == 'same':
        con1 = nowAoi != riderAoi
        con2 = nowAoi != -1
        con3 = riderId not in dataSaver.superDic
        if con1 and con2 and con3:
            outScore += Config.score_not_same_aoi*1
    else:
        con1 = userAoi == riderAoi
        con2 = riderId in dataSaver.superDic
        if con1 or con2:
            outScore += Config.score_same_aoi_small*1
    # 如果是超级骑士，给单之后，无法及时完成身上所挂的超级预约单，减分
    if riderId in dataSaver.superDic:
        ifFinish = super_finish(dataSaver, riderId, timeUse, riderUseX, riderUseY, riderSpeed)
        if not ifFinish:
            outScore += Config.score_cannot_super*1
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
    disScore = 1-shopRiderDis/float(1000)
    if disScore < -1:
        disScore = -1
    return disScore

def exact_finish(
        timeUse, riderSpeed, riderUseX,
        riderUseY, userX, userY, shopX,
        shopY, expectTime, waitTime, timer,
        timeNow, orderTime
        ):
    '''
    骑士可以准时送达和骑士完成所需时间
    '''
    exactScore = 0
    timeScore = 0
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
    waitShopTime = timer.add_second_datetime(
            timer.trans_unix_to_datetime(orderTime), waitTime
            )
    # 可以完成时间
    if atShopTime >= waitShopTime:
        finishTime = timer.add_second_datetime(atShopTime, shopToUser)
    else:
        finishTime = timer.add_second_datetime(waitShopTime, shopToUser)
    if timer.add_second_datetime(expectTime, Config.putong_wait) > finishTime:
        exactScore = 1
    # 完成所需时间
    totalTime = (finishTime-timer.trans_unix_to_datetime(timeNow)).seconds
    timeScore = 1-totalTime/60.0/30.0
    if timeScore < -1:
        timeScore = -1
    return exactScore, timeScore


def super_finish(dataSaver, riderId, timeUse, riderUseX, riderUseY, riderSpeed):
    '''
    挂给骑士一单后，是否还能准时完成身上的预约单
    '''
    ifFinish = False
    orderId = dataSaver.superDic[riderId]['orderId']
    orderDic = dataSaver.superOrderDic[orderId]
    expectTime = dataSaver.superDic[riderId]['expectTime']
    userX = orderDic['userMcx']
    userY = orderDic['userMcy']
    # 骑士到super用户所需要的时间
    goUserTime = math.ceil(
            base_few.Mercator.getDistance(
                [float(userX), float(userY)],
                [float(riderUseX), float(riderUseY)],
                )/float(riderSpeed)
            )
    if expectTime>timeUse:
        # super单还剩余多长时间
        resTime = (
                dataSaver.timer.trans_unix_to_datetime(expectTime)-
                dataSaver.timer.trans_unix_to_datetime(timeUse)
                ).seconds
        # 判断派给此单之后，还能否完成
        if resTime>=Config.super_go_give:
            if goUserTime<=Config.super_go_give+Config.putong_wait:
                ifFinish = True
        else:
            if goUserTime<=resTime+Config.putong_wait:
                ifFinish = True
        return ifFinish
