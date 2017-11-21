# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys

import Config
sys.path.append(Config.base_few_path)
import base_few


def cal_order_similar(orderOne, orderTwo, dataSaver):
    '''
    计算仅仅两个订单之间的相似度
    '''
    score = 0
    # 获取数据
    shop1X = orderOne['shopMcx']
    shop1Y = orderOne['shopMcy']
    shop2X = orderTwo['shopMcx']
    shop2Y = orderTwo['shopMcy']
    user1X = orderOne['userMcx']
    user1Y = orderOne['userMcy']
    user2X = orderTwo['userMcx']
    user2Y = orderTwo['userMcy']
    yuding1 = orderOne['expectTime']
    yuding2 = orderTwo['expectTime']
    # 不合并预订单
    if (not yuding1) or (not yuding2):
        score += 1*Config.similar_weight_yuding
    # 同店同用户
    con1 = shop1X == shop2X
    con2 = shop1Y == shop2Y
    con3 = user1X == user2X
    con4 = user1Y == user2Y
    if con1 and con2 and con3 and con4:
        score += 1*Config.similar_weight_same_shop_user
    # 商户之间距离比较近(-1,1)
    shopDis = base_few.Mercator.getDistance(
            (float(shop1X), float(shop1Y)),
            (float(shop2X), float(shop2Y))
            )
    shopRatio = (Config.similar_shop_dis_thres-shopDis)/Config.similar_shop_dis_thres
    if shopRatio < -1:
        shopRatio = -1
    score += Config.similar_weight_shop*shopRatio
    # 用户之间距离比较近
    userDis = base_few.Mercator.getDistance(
            (float(user1X), float(user1Y)),
            (float(user2X), float(user2Y)),
            )
    userRatio = (Config.similar_user_dis_thres-userDis)/Config.similar_user_dis_thres
    if userRatio < -1:
        userRatio = -1
    score += Config.similar_weight_user*userRatio
    # 空间收益，在路程上是否有剩余
    shop1user1 = base_few.Mercator.getDistance(
            (float(shop1X), float(shop1Y)),
            (float(user1X), float(user1Y)),
            )
    shop1user2 = base_few.Mercator.getDistance(
            (float(shop1X), float(shop1Y)),
            (float(user2X), float(user2Y)),
            )
    shop2user1 = base_few.Mercator.getDistance(
            (float(shop2X), float(shop2Y)),
            (float(user1X), float(user1Y)),
            )
    shop2user2 = base_few.Mercator.getDistance(
            (float(shop2X), float(shop2Y)),
            (float(user2X), float(user2Y)),
            )
    income = (shop1user1+shop2user2)-(userDis+shopDis+min(shop1user1, shop1user2, shop2user1, shop2user2))
    if income > Config.similar_income_thres:
        income = Config.similar_income_thres
    incomeRatio = income/Config.similar_income_thres
    if incomeRatio < -1:
        incomeRatio = -1
    score += incomeRatio*Config.similar_weight_income
    # 并单后，骑士配送是否会超时
    ifFinish = if_chaoshi(
            dataSaver, orderOne, orderTwo, shopDis, userDis,
            shop1user1, shop1user2, shop2user1, shop2user2
            )
    if not ifFinish:
        score += Config.similar_weight_cannot_finish
    return score


def if_chaoshi(
        dataSaver, orderOne, orderTwo, shopDis, userDis,
        shop1user1, shop1user2, shop2user1, shop2user2,
        ):
    '''
    判断并单之后，骑士送是否会超时
    '''
    ifFinish = 0
    riderSpeed = 4.0
    nowTime = dataSaver.timer.trans_unix_to_datetime(dataSaver.time)
    orderTime1 = dataSaver.timer.trans_unix_to_datetime(orderOne['orderTime'])
    orderTime2 = dataSaver.timer.trans_unix_to_datetime(orderTwo['orderTime'])
    expectTime1 = dataSaver.timer.trans_unix_to_datetime(orderOne['expectTime'])
    expectTime2 = dataSaver.timer.trans_unix_to_datetime(orderTwo['expectTime'])
    waitTime1 = orderOne['waitSecs']
    waitTime2 = orderTwo['waitSecs']
    goShopRange = 1000/riderSpeed
    # 走shop1，再走shop2，所需要取餐完成时间
    atShopTime = dataSaver.timer.add_second_datetime(nowTime, goShopRange)
    chucanTime = dataSaver.timer.add_second_datetime(orderTime1, waitTime1)
    goShopTime = 0
    if atShopTime > chucanTime:
        goShopTime = atShopTime
    else:
        goShopTime = chucanTime
    betweenTime = shopDis/riderSpeed
    atShopTime = dataSaver.timer.add_second_datetime(goShopTime, betweenTime)
    chucanTime = dataSaver.timer.add_second_datetime(orderTime2, waitTime2)
    finish1Time = 0
    if atShopTime > chucanTime:
        finish1Time = atShopTime
    else:
        finish1Time = chucanTime
    # 走shop2，再走shop1，所需要取餐完成时间
    atShopTime = dataSaver.timer.add_second_datetime(nowTime, goShopRange)
    chucanTime = dataSaver.timer.add_second_datetime(orderTime2, waitTime2)
    goShopTime = 0
    if atShopTime > chucanTime:
        goShopTime = atShopTime
    else:
        goShopTime = chucanTime
    betweenTime = shopDis/riderSpeed
    atShopTime = dataSaver.timer.add_second_datetime(goShopTime, betweenTime)
    chucanTime = dataSaver.timer.add_second_datetime(orderTime1, waitTime1)
    finish2Time = 0
    if atShopTime > chucanTime:
        finish2Time = atShopTime
    else:
        finish2Time = chucanTime
    # 最终到达用户时间
    if finish1Time >= finish2Time:
        routeList = [shop1user1, shop1user2]
        minIndex = routeList.index(min(routeList))
        atUserTime = dataSaver.timer.add_second_datetime(
                finish2Time, routeList[minIndex]/riderSpeed
                )
        atUserTime2 = dataSaver.timer.add_second_datetime(
                atUserTime, userDis/riderSpeed
                )
        if minIndex == 0:
            con1 = atUserTime < expectTime1
            con2 = atUserTime2 < expectTime2
            if con1 and con2:
                ifFinish = 1
        else:
            con1 = atUserTime < expectTime2
            con2 = atUserTime2 < expectTime1
            if con1 and con2:
                ifFinish = 1
    else:
        routeList = [shop2user1, shop2user2]
        minIndex = routeList.index(min(routeList))
        atUserTime = dataSaver.timer.add_second_datetime(
                finish1Time, routeList[minIndex]/riderSpeed
                )
        atUserTime2 = dataSaver.timer.add_second_datetime(
                atUserTime, userDis/riderSpeed
                )
        if minIndex == 0:
            con1 = atUserTime < expectTime1
            con2 = atUserTime2 < expectTime2
            if con1 and con2:
                ifFinish = 1
        else:
            con1 = atUserTime < expectTime2
            con2 = atUserTime2 < expectTime1
            if con1 and con2:
                ifFinish = 1
    return ifFinish
