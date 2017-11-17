# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
from tools import base_few


if __name__ == '__main__':
    table = base_few.DaoBase(
            host='127.0.0.1',
            port=3306,
            user='root',
            passwd='hui182014734',
            db='wuliu',
            table='delivery_moniter'
            )
    print(table.run_sql('select count(rider_id) from rider'))
