# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import math
import sys
sys.path.append('../../')

import Config
from .. import base_few


class OperRecorder():
    '''
    对骑士行驶路径，需要执行的操作，进行计算
    '''
    def __init__(self):
        self.fileWriter1 = open(Config.oper_info_total_path, 'wb')

    def init_value(self):
        self.fileWriter = open(Config.oper_info_path, 'wb')

    def update_riderFrame(self, dataSaver):
        '''
        对骑士1分钟变化的信息进行更新
        '''
        timer = base_few.Timer()
        riderIdList = dataSaver.riderFrame.keys()
        for riderId in riderIdList:
            # 获取数据
            riderStatus = dataSaver.riderFrame[riderId]['status']
            hasOrderNum = dataSaver.riderFrame[riderId]['hasOrderNum']
            orderList= dataSaver.riderFrame[riderId]['orderList']
            finishTime = dataSaver.riderFrame[riderId]['finishTime']
            nowTime = dataSaver.time
            # 空闲骑士接单变为有单骑士
            con1 = riderStatus == 'leisure'
            con2 = hasOrderNum > 0
            if con1 and con2:
                orderId = orderList[0]
                finishTime = self.finish_time(dataSaver, riderId, orderId, timer)
                dataSaver.rider_status_from_leisure_to_processing(
                        riderId, orderId, finishTime
                        )
            # 骑士正在送一单
            con1 = riderStatus == 'processing'
            if con1:
                # 检查骑士此单是否送完
                finishTime = timer.trans_unix_to_datetime(finishTime)
                nowTime = timer.trans_unix_to_datetime(nowTime)
                if nowTime >= finishTime:
                    # 此订单已被配送完成
                    if len(orderList) == 0:
                        # 身上没有其他配送的订单了
                        status = 'leisure'
                        dataSaver.rider_status_finish(riderId, status)
                    else:
                        # 更改已完成状态
                        status = 'processing'
                        dataSaver.rider_status_finish(riderId, status)
                        # 更改新订单状态
                        orderId = orderList[0]
                        finishTime = self.finish_time(dataSaver, riderId, orderId, timer)
                        dataSaver.rider_status_from_leisure_to_processing(
                                riderId, orderId, finishTime
                                )


    def __write_info(self, rider_id, rider_2_id, order_id, mcx, mcy, t, action):
        self.fileWriter.write(
                '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    rider_id,
                    rider_2_id,
                    order_id,
                    mcx,
                    mcy,
                    t,
                    action
                    ).encode('utf8')
                )
        self.fileWriter1.write(
                '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    rider_id,
                    rider_2_id,
                    order_id,
                    mcx,
                    mcy,
                    t,
                    action
                    ).encode('utf8')
                )

    def finish_time(self, dataSaver, riderId, orderId, timer):
        '''
        计算骑士开始配送之后可以完成的时间
        '''
        #
        riderX = dataSaver.riderFrame[riderId]['mcx']
        riderY = dataSaver.riderFrame[riderId]['mcy']
        riderSpeed = float(dataSaver.riderFrame[riderId]['speed'])
        orderDic = dataSaver.fenpeiDic[orderId]
        orderTime = orderDic['orderTime']
        userX = orderDic['userMcx']
        userY = orderDic['userMcy']
        mealTime = orderDic['waitSecs']
        shopX = orderDic['shopMcx']
        shopY = orderDic['shopMcy']
        #
        orderTime = timer.trans_unix_to_datetime(orderTime)
        nowTime = timer.trans_unix_to_datetime(dataSaver.time)
        # 计算到达商户取出餐的时间
        goShop = math.ceil(
                base_few.Mercator.getDistance(
                    [float(riderX), float(riderY)], [float(shopX), float(shopY)])/riderSpeed
                )
        goShopTime = timer.add_second_datetime(nowTime, goShop)
        goMealTime = timer.add_second_datetime(orderTime, mealTime)
        if goShopTime > goMealTime:
            shopTime = goShopTime
        else:
            shopTime = goMealTime
        # 计算取到餐到用户的时间
        goUser = math.ceil(
                base_few.Mercator.getDistance(
                    [float(shopX), float(shopY)], [float(userX), float(userY)])/riderSpeed
                )
        goUserTime = timer.add_second_datetime(shopTime, goUser)
        finishTime = timer.trans_datetime_to_unix(goUserTime)
        # 写此次信息
        self.__write_info(riderId, '', orderId, riderX, riderY, dataSaver.time, '0')
        self.__write_info(
                riderId, '', orderId, shopX, shopY, timer.trans_datetime_to_unix(shopTime), '1'
                )
        self.__write_info(riderId, '', orderId, userX, userY, finishTime, '3')
        return finishTime
