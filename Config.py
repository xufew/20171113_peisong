# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import os


ABS_PATH=os.path.dirname(
        os.path.abspath(__file__)
        )

# 拉取订单间隔(秒)
order_time_range = 60

# 相似度阈值distance
similar_shop_distance_thres = 1000
similar_user_distance_thres = 1000
similar_user_weight = 0.3
similar_shop_weight = 0.7

# 并单最大组合阈值
combine_thres = 5

# 输出骑士操作信息路径
oper_info_path = '{}/out/oper_info'.format(ABS_PATH)
oper_info_total_path = '{}/out/oper_info_total'.format(ABS_PATH)
oper_info_test = '{}/out/oper_info_test'.format(ABS_PATH)
