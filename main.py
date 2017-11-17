# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import time

import pandas as pd

from tools import wuliu
from munkres import Munkres


def time_now():
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))


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
    # 获取一分钟订单
    while True:
    # for i in range(1):
        if producer.time >= producer.endtime:
            break
        # 取信息,每分钟的订单
        orderValue = producer.produce_order()
        dataSaver.save_order_info(orderValue)
        dataSaver.time = producer.time
        print(len(dataSaver.orderDic))
        # # 进行订单合并
        # similarSet = orderProcesser.combine_order_firstime(
        #         dataSaver.orderDic,
        #         dataSaver.riderFrame,
        #         )
        # # 进行订单分配给骑士中含有相似订单
        # similarSet = dispatcher.rider_similar_order(
        #         similarSet, dataSaver
        #         )
        similarSet = []
        # 空闲骑士和订单之间进行打分矩阵的计算
        dispatcher.init_value()
        ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                dataSaver.orderDic, dataSaver.riderFrame,
                similarSet, 'free', 'same'
                )
        # 将订单分配给空闲骑士
        if ifHas:
            for aoiId in orderRiderMatrix:
                dispatcher.Km_dispatch(
                        pd.DataFrame(orderRiderMatrix[aoiId]).T, dataSaver, munkreser
                        )
        # 计算非空闲骑士
        dispatcher.init_value()
        ifHas, orderRiderMatrix = dispatcher.rider_order_matrix(
                dataSaver.orderDic, dataSaver.riderFrame,
                similarSet, 'processing', 'same'
                )
        if ifHas:
            for aoiId in orderRiderMatrix:
                dispatcher.Km_dispatch(
                        pd.DataFrame(orderRiderMatrix[aoiId]).T, dataSaver, munkreser
                        )
        # 开始处理骑士已分配单的取放
        operRecorder.init_value()
        operRecorder.update_riderFrame(dataSaver)
        operRecorder.fileWriter.close()
        # 上传本次任务信息
        producer.post_trace()
    dataSaver.test_save()
