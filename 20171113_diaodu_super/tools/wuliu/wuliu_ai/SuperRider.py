# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import math
import sys

import Config
sys.path.append(Config.base_few_path)
import base_few


def choose_rider(orderDic, riderFrame, timer, timeNow, superDic):
    '''
    进行super rider的选择
    '''
    chooseDic = {}
    for orderId in orderDic:
        thisOrderDic = orderDic[orderId]
        shopMcx = thisOrderDic['shopMcx']
        shopMcy = thisOrderDic['shopMcy']
        waitSecs = thisOrderDic['waitSecs']
        orderTime = timer.trans_unix_to_datetime(thisOrderDic['orderTime'])
        expectTime = timer.trans_unix_to_datetime(thisOrderDic['expectTime'])
        orderAoi = thisOrderDic['userAoi']
        nowTime = timer.trans_unix_to_datetime(timeNow)
        # 开始计算订单得满足的条件
        totalSec = (expectTime-nowTime).seconds
        con1 = waitSecs < Config.super_yuding_wait_time         # 预约单等餐时间必须小
        con2 = totalSec > Config.super_yuding_total_time        # 预约单时间必须够大
        if con1 and con2:
            timeDic = {}
            speedDic = {}
            for riderId in riderFrame:
                riderAoi = riderFrame[riderId]['aoiId']
                riderStatus = riderFrame[riderId]['status']
                con1 = riderId in superDic          # 已经是超级骑士，不进入选择
                con2 = riderStatus != 'leisure'     # 空闲骑士，才能变为超级骑士
                con3 = orderAoi != riderAoi         # 超级骑士，必须挂本商圈单
                if con1 or con2 or con3:
                    continue
                thisRiderDic = riderFrame[riderId]
                riderX = thisRiderDic['mcx']
                riderY = thisRiderDic['mcy']
                status = thisRiderDic['status']
                speed = thisRiderDic['speed']
                useTime = math.ceil(
                        base_few.Mercator.getDistance(
                            (float(shopMcx), float(shopMcy)),
                            (float(riderX), float(riderY)),
                            )/float(speed)
                        )
                timeDic[riderId] = useTime
                speedDic[riderId] = speed
            if len(timeDic) == 0:
                # 没有符合可以变的超级骑士
                continue
            minId = min(timeDic, key=timeDic.get)
            # 计算需要存储的数据
            atShopTime = timer.add_second_datetime(
                    timer.trans_unix_to_datetime(timeNow),
                    timeDic[minId]
                    )
            waitTime = timer.add_second_datetime(orderTime, waitSecs)
            if atShopTime >= waitTime:
                useTime = atShopTime
            else:
                useTime = waitTime
            chooseDic[minId] = {
                    'orderId': orderId,
                    'expectTime': timer.trans_datetime_to_unix(expectTime),
                    'atShopTime': timer.trans_datetime_to_unix(useTime),
                    'acceptTime': timeNow
                    }
    return chooseDic
