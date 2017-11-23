# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import sys
import time

import pandas as pd

from tools import wuliu
from munkres import Munkres
import Config


def time_now():
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))


def get_free_rider_num(dataSaver):
    useFrame = pd.DataFrame(dataSaver.riderFrame).T
    freeRiderFrame = useFrame.loc[useFrame.loc[:, 'status'] == 'leisure', :]
    riderList = list(freeRiderFrame.index)
    return len(riderList)


def set_produce_order_num(orderSer, producer):
    setNum = 60
    nowTime = producer.time
    nextTime = producer.timer.trans_datetime_to_unix(
            producer.timer.add_second_datetime(
                producer.timer.trans_unix_to_datetime(nowTime),
                Config.order_time_count
                )
            )
    con1 = orderSer.index>nowTime
    con2 = orderSer.index<=nextTime
    orderValue = orderSer[con1&con2].values[0]
    if orderValue == 0:
        setNum = Config.order_time_count
    elif orderValue <= 3:
        setNum = 1
    elif orderValue <= 7:
        setNum = 60
    else:
        setNum = 60
    return setNum


if __name__ == '__main__':
    # 订单初始化
    producer = wuliu.DataProducer()                 # 初始化数据生成器
    dataSaver = wuliu.DataSaver()                   # 初始化数据存储器
    orderProcesser = wuliu.OrderProcesser()         # 初始化订单处理器
    dispatcher = wuliu.Dispatcher()                 # 初始化订单指派器
    operRecorder = wuliu.OperRecorder()             # 初始化骑士操作记录器
    munkreser = Munkres()                           # 初始化KM规划计算
    # 第一次获取所有骑士的信息并储存(dataSaver.riderFrame)
    riderValue = producer.produce_rider()
    dataSaver.save_rider_info(riderValue)
    # 获取首次出单时间, 并将时间计时器设置为此时间
    producer.count_first_time()
    # 计算时间订单分布，确定满足10单和商圈时间
    producer.count_data_dis()
    # 计算订单分布，用以定义压单量
    orderSer = producer.count_order_dis()
    while True:
    # for i in range(1):
        if producer.time >= producer.endtime:
            break
        # 初始化变量
        operRecorder.init_value()
        # 计算商圈压力，并设置对应的压单量
        setNum = set_produce_order_num(orderSer, producer)
        # setNum = 3000
        orderValue = producer.produce_order(setNum)
        # 取信息,每分钟的订单
        dataSaver.time = producer.time
        dataSaver.save_order_info(orderValue)
        # 检查是否有预约单可以进入派单流程
        dataSaver.check_yuyue_order()
        # 进行追加，正在配送中的订单
        dispatcher.dispatch_add(dataSaver, operRecorder)
        orderNum = len(dataSaver.orderDic)
        print(orderNum)
        if orderNum > 0:
            # 是否进行订单合并
            similarSet = []
            if get_free_rider_num(dataSaver) < 0:
                similarSet = orderProcesser.combine_order(
                        dataSaver
                        )
            else:
                pass
            if producer.time > producer.changeTime:
                # 空闲骑士和订单之间进行打分矩阵的计算
                dispatcher.init_value()
                dispatcher.typeDic['riderType'] = 'free'
                dispatcher.typeDic['aoiType'] = 'same'
                dispatcher.typeDic['minNumType'] = 'first'
                ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                        dataSaver, similarSet
                        )
                # 将订单分配给空闲骑士
                if ifHas:
                    for aoiId in orderRiderMatrix:
                        dispatcher.Km_dispatch(
                                orderRiderMatrix[aoiId],
                                dataSaver,
                                munkreser,
                                similarSet
                                )
                # 计算非空闲骑士
                dispatcher.init_value()
                dispatcher.typeDic['riderType'] = 'processing'
                dispatcher.typeDic['aoiType'] = 'same'
                dispatcher.typeDic['minNumType'] = 'first'
                ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                        dataSaver, similarSet
                        )
                if ifHas:
                    for aoiId in orderRiderMatrix:
                        dispatcher.Km_dispatch(
                                orderRiderMatrix[aoiId],
                                dataSaver,
                                munkreser,
                                similarSet
                                )
            else:
                # 空闲骑士和订单之间进行打分矩阵的计算
                dispatcher.init_value()
                dispatcher.typeDic['riderType'] = 'free'
                dispatcher.typeDic['aoiType'] = 'same'
                dispatcher.typeDic['minNumType'] = 'last'
                ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                        dataSaver, similarSet
                        )
                # 将订单分配给空闲骑士
                if ifHas:
                    for aoiId in orderRiderMatrix:
                        dispatcher.Km_dispatch(
                                orderRiderMatrix[aoiId],
                                dataSaver,
                                munkreser,
                                similarSet
                                )
                # 计算非空闲骑士
                dispatcher.init_value()
                dispatcher.typeDic['riderType'] = 'processing'
                dispatcher.typeDic['aoiType'] = 'same'
                dispatcher.typeDic['minNumType'] = 'last'
                ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                        dataSaver, similarSet
                        )
                if ifHas:
                    for aoiId in orderRiderMatrix:
                        dispatcher.Km_dispatch(
                                orderRiderMatrix[aoiId],
                                dataSaver,
                                munkreser,
                                similarSet
                                )
        # 开始处理骑士已分配单的取放
        operRecorder.update_riderFrame(dataSaver)
        operRecorder.fileWriter.close()
        # 上传本次任务信息
        producer.post_trace()
