# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import math

import base_few


def if_add_order(
        orderId, riderId, riderDic, orderDic, userNewX,
        userNewY, waitTime, orderAoi, timer, nowTime
        ):
    '''
    是否对骑士进行追加订单
    '''
    ifAdd = False
    thisRider = riderDic[riderId]
    if thisRider['status'] == 'processing':
        shopX = orderDic[orderId]['shopMcx']
        shopY = orderDic[orderId]['shopMcy']
        orderTime = orderDic[orderId]['orderTime']
        routeDic = thisRider['routeDic']
        orderShop = '{}_{}'.format(shopX, shopY)
        riderAoi = thisRider['aoiId']
        orderNum = len(thisRider['processOrder'])
        # 先判断追加订单商户，是否在次骑士运行的路径中, 同商圈
        con1 = orderShop in routeDic['shopRoute']
        con2 = orderAoi == riderAoi
        con3 = orderNum<6
        if con1 and con2 and con3:
            # 判断此骑士到达此商户时，此订单是否能出餐
            atShopTime = timer.trans_unix_to_datetime(
                    routeDic['shopRoute'][orderShop]
                    )
            chucanTime = timer.add_second_datetime(
                    timer.trans_unix_to_datetime(orderTime),
                    waitTime
                    )
            if atShopTime >= chucanTime:
                # 判断此骑士配送，和分配给别的骑士配送的收益
                routeDesUser = max(
                        routeDic['userRoute'],
                        key=routeDic['userRoute'].get
                        )
                userDesX = routeDesUser.split('_')[0]
                userDesY = routeDesUser.split('_')[1]
                userDesTime = routeDic['userRoute'][routeDesUser]
                # 计算加给此骑士，送达用户的时间
                deltaDis = base_few.Mercator.getDistance(
                        [float(userDesX), float(userDesY)],
                        [float(userNewX), float(userNewY)]
                        )
                riderSpeed = float(thisRider['speed'])
                newDesTime = timer.trans_datetime_to_unix(
                        timer.add_second_datetime(
                            timer.trans_unix_to_datetime(userDesTime),
                            math.ceil(deltaDis/riderSpeed)
                            )
                        )
                # 计算分配给其他骑士，此单完成时间
                riderX = thisRider['mcx']
                riderY = thisRider['mcy']
                totalDis = base_few.Mercator.getDistance(
                        [float(riderX), float(riderY)],
                        [float(shopX), float(shopY)]
                        ) + base_few.Mercator.getDistance(
                                [float(shopX), float(shopY)],
                                [float(userNewX), float(userNewY)],
                                )
                abTime = timer.trans_datetime_to_unix(
                        timer.add_second_datetime(
                            timer.trans_unix_to_datetime(nowTime),
                            totalDis/riderSpeed
                            )
                        )
                if (newDesTime <= abTime):
                    # 如果另分配一个骑士，不如切单速度快，选择切单
                    ifAdd = True
    if ifAdd:
        return ifAdd, (
            userNewX, userNewY, timer.trans_datetime_to_unix(atShopTime), newDesTime
            )
    else:
        return ifAdd, ()
