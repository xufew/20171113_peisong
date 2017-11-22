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
change_time_thres = 1                           # 保留多少单进入局部最优,骑士总数倍数
yuding_time_thres = 1500                        # 预订单离预期时间剩多久进入派单流程
yuding_wait = 300                               # 预订单不能在这之前完成
putong_wait = 300                               # 大于多少秒算超时

# 订单相似度
similar_weight_same_shop_user = 3
similar_shop_dis_thres = 500.0                  # 商户之间比较近的阈值
similar_weight_shop = 1
similar_user_dis_thres = 500.0                  # 用户之间比较近的阈值
similar_weight_user = 1
similar_income_thres = 1000.0                   # 空间距离收益阈值
similar_weight_income = 1
similar_weight_cannot_finish = -3               # 合并之后无法完成订单
similar_weight_yuding = -100                    # 预订单不进行合并

# 并单最大组合阈值
combine_thres = 4
combine_score_thres = 2.5

# 骑士打分权重
score_distance = 1
score_not_ten = 8
score_exact_finish = 3
score_time_score = 2
score_not_same_aoi = 8
