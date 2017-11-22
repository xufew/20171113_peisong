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
from .wuliu_ai import Tsp


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
            processOrder = dataSaver.riderFrame[riderId]['processOrder']
            nowTime = dataSaver.time
            # 空闲骑士接单变为有单骑士
            con1 = riderStatus == 'leisure'
            con2 = hasOrderNum > 0
            if con1 and con2:
                finishTime, desX, desY, desAoi = self.finish_time(
                        dataSaver, riderId, orderList, timer
                        )
                dataSaver.rider_status_from_leisure_to_processing(
                        riderId, orderList, finishTime,
                        desX, desY, desAoi
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
                        finishTime, desX, desY, desAoi = self.finish_time(
                                dataSaver, riderId, orderList, timer
                                )
                        dataSaver.rider_status_from_leisure_to_processing(
                                riderId, orderList, finishTime,
                                desX, desY, desAoi
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

    def finish_time(self, dataSaver, riderId, orderList, timer):
        '''
        计算骑士开始配送之后可以完成的时间
        '''
        #
        if len(orderList) == 1:
            # 如果此骑士要接受的订单是个单订单， 计算骑士的完成时间
            # 并进行订单路径的计算存储
            orderId = orderList[0]
            riderX = dataSaver.riderFrame[riderId]['mcx']
            riderY = dataSaver.riderFrame[riderId]['mcy']
            riderSpeed = float(dataSaver.riderFrame[riderId]['speed'])
            orderDic = dataSaver.fenpeiDic[orderId]
            orderTime = orderDic['orderTime']
            userX = orderDic['userMcx']
            userY = orderDic['userMcy']
            userAoi = orderDic['userAoi']
            mealTime = orderDic['waitSecs']
            shopX = orderDic['shopMcx']
            shopY = orderDic['shopMcy']
            immediateDeliver = orderDic['immediateDeliver']
            expectTime = orderDic['expectTime']
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
            # 如果此单为预约单，判断是否在5分钟前完成，如果是，则拖后完成时间
            if not immediateDeliver:
                expectTime = timer.trans_unix_to_datetime(expectTime)
                if expectTime>goUserTime:
                    delt = (expectTime-goUserTime).seconds
                    if delt >= Config.yuding_wait:
                        finishTime = timer.trans_datetime_to_unix(
                                timer.add_second_datetime(expectTime, -Config.yuding_wait)
                                )
            # 写此次信息
            self.__write_info(riderId, '', orderId, riderX, riderY, dataSaver.time, '0')
            self.__write_info(
                    riderId, '', orderId, shopX, shopY, timer.trans_datetime_to_unix(shopTime), '1'
                    )
            dataSaver.riderFrame[riderId]['routeDic']['shopRoute'][
                    '{}_{}'.format(shopX, shopY)
                    ] = timer.trans_datetime_to_unix(shopTime)
            self.__write_info(riderId, '', orderId, userX, userY, finishTime, '3')
            dataSaver.riderFrame[riderId]['routeDic']['userRoute'][
                    '{}_{}'.format(userX, userY)
                    ] = finishTime
            # 确定结束信息
            desX = userX
            desY = userY
            desAoi = userAoi
        elif len(orderList) > 1:
            # 派给的订单是一个订单组
            riderShop, shopUser = Tsp.tsp_greedy(orderList, riderId, dataSaver)
            # 获取数据
            riderX = dataSaver.riderFrame[riderId]['mcx']
            riderY = dataSaver.riderFrame[riderId]['mcy']
            riderSpeed = float(dataSaver.riderFrame[riderId]['speed'])
            nowTime = dataSaver.time
            # 走商户取餐
            for orderId in riderShop:
                self.__write_info(riderId, '', orderId, riderX, riderY, nowTime, '0')
                orderDic = dataSaver.fenpeiDic[orderId]
                shopX = orderDic['shopMcx']
                shopY = orderDic['shopMcy']
                thisWait = orderDic['waitSecs']
                thisDis = base_few.Mercator.getDistance(
                        (float(riderX), float(riderY)), (float(shopX), float(shopY))
                        )
                atShopTime = timer.add_second_datetime(
                        timer.trans_unix_to_datetime(nowTime),
                        math.ceil(thisDis/float(riderSpeed)),
                        )
                waitTime = timer.add_second_datetime(
                        timer.trans_unix_to_datetime(nowTime),
                        thisWait
                        )
                if atShopTime > waitTime:
                    nowTime = timer.trans_datetime_to_unix(atShopTime)
                else:
                    nowTime = timer.trans_datetime_to_unix(waitTime)
                riderX = shopX
                riderY = shopY
                self.__write_info(riderId, '', orderId, riderX, riderY, nowTime, '1')
                dataSaver.riderFrame[riderId]['routeDic']['shopRoute'][
                        '{}_{}'.format(riderX, riderY)
                        ] = nowTime
            # 开始从商户送给用户
            for orderId in shopUser:
                orderDic = dataSaver.fenpeiDic[orderId]
                userX = orderDic['userMcx']
                userY = orderDic['userMcy']
                thisDis = base_few.Mercator.getDistance(
                        (float(riderX), float(riderY)), (float(userX), float(userY))
                        )
                nowTime = timer.trans_datetime_to_unix(
                        timer.add_second_datetime(
                            timer.trans_unix_to_datetime(nowTime),
                            math.ceil(thisDis/float(riderSpeed))
                            )
                        )
                riderX = userX
                riderY = userY
                self.__write_info(riderId, '', orderId, riderX, riderY, nowTime, '3')
                dataSaver.riderFrame[riderId]['routeDic']['userRoute'][
                        '{}_{}'.format(riderX, riderY)
                        ] = nowTime
            # 最终赋值
            finishTime = nowTime
            desX = riderX
            desY = riderY
            desAoi = orderDic['userAoi']
        return finishTime, desX, desY, desAoi
