# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import os


ABS_PATH=os.path.dirname(
        os.path.abspath(__file__)
        )
# 包路径
base_few_path='{}/{}'.format(ABS_PATH, 'tools')
# 输出骑士操作信息路径
oper_info_path = '{}/out/oper_info'.format(ABS_PATH)
oper_info_total_path = '{}/out/oper_info_total'.format(ABS_PATH)
oper_info_test = '{}/out/oper_info_test'.format(ABS_PATH)

# 拉取订单间隔(秒)
order_time_range = 60
order_time_count = 60                           # 计算dis分布的时间间隔
change_rider_Num = 500                          # 剩多少订单，可以进入满足10单的要求
yuding_time_thres = 1550                        # 预订单离预期时间剩多久进入派单流程
yuding_wait = 300                               # 预订单不能在这之前完成
putong_wait = 299                               # 大于多少秒算超时

# 追加订单距离阈值
add_weight_dis_thres = 500

# 订单相似度
similar_weight_same_shop_user = 3.1
similar_shop_dis_thres = 500.0                  # 商户之间比较近的阈值
similar_weight_shop = 0
similar_user_dis_thres = 500.0                  # 用户之间比较近的阈值
similar_weight_user = 0
similar_income_thres = 1000.0                   # 空间距离收益阈值
similar_weight_income = 0
similar_weight_cannot_finish = 0               # 合并之后无法完成订单
similar_weight_yuding = -100                    # 预订单不进行合并

# 并单最大组合阈值
combine_thres = 3
combine_score_thres = 3

# 骑士打分权重
score_distance = 0
score_not_ten = 8
score_not_ten_small = 0.5
score_exact_finish = 3
score_time_score = 3
score_not_same_aoi = 8
score_same_aoi_small = 2
score_order_time = 0
score_free = 2
score_speed = -0.5
score_cannot_super = -100

# 超级骑士
super_yuding_total_time = 7200                  # 预定时间要大，才值得骑士去做
super_yuding_wait_time = 1800
super_go_give = 3600                            # 订单还剩多长时间去送
