# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import pymysql


class DaoBase:
    '''
    数据库封装类
    '''
    def __init__(self, host, port, user, passwd, db, table):
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.db = db
        self.table = table
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                port=self.port,
                charset='utf8'
                )
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def getKeyValueStr(self, conds, delimeter=' and '):
        cond_str = ''
        if (isinstance(conds, list) and len(conds) != 0):
            cond_str = delimeter.join(conds)
        elif (isinstance(conds, dict) and len(conds) != 0):
            cond_list = []
            for k, v in dict.iteritems():
                cond_list.append(k + '=' + v)
            cond_str = delimeter.join(cond_list)
        return cond_str

    def select(self, fields, conds, options=None, appends=None):
        field_str = ','.join(fields)
        cond_str = self.getKeyValueStr(conds, ' and ')
        last_str = ''
        if (isinstance(options, list) and len(options) != 0):
            last_str = ' '.join(options)
        if (isinstance(appends, list) and len(appends) != 0):
            last_str = last_str + ' '.join(appends)

        where_str = ''
        if (len(cond_str) != 0):
            where_str = ' where ' + cond_str
        query = 'select ' + field_str + ' from ' + self.table + where_str + ' ' + last_str
        self.cursor.execute(query)
        outResult = self.cursor.fetchall()
        return outResult

    def update(self, fields, conds):
        field_str = self.getKeyValueStr(fields, ',')
        cond_str  = self.getKeyValueStr(conds, ' and ')

        where_str = ''
        if (len(cond_str) != 0):
            where_str = ' where ' + cond_str
        query = 'update ' + self.table + ' set ' + field_str + where_str
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    def run_sql(self, sql):
        '''
        运行原生态的sql语句
        '''
        self.cursor.execute(sql)
        self.conn.commit()
        outResult = self.cursor.fetchall()
        return outResult


if __name__ == '__main__':
    table = DaoBase(
            host='10.195.217.23',
            port=6670,
            user='tanxing',
            passwd='UrOqcEEjxfFc',
            db='waimai_anticheat',
            table='delivery_moniter'
            )
    fields = ['delivery_id', 'qishi_name', 'dt']
    conds = ['delivery_id = 4272']
    ret = table.select(fields, conds)
    for row in ret:
        id = row[0]
        name = row[1]
        print(str(id) + "\t" + name)
    conds = ['delivery_id = 1475158720']
    ret = table.select(fields, conds)
    for row in ret:
        id = row[0]
        name = row[1]
        print(str(id) + "\t" + name)
