# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import configparser

from . import Bns


class Config_Parser:
    '''
    读取config里面的配置文件，并返回相对应的东西
    Config_Parser(path)
    '''
    def __init__(self, path):
        self.path = path
        self.cf = configparser.ConfigParser()
        self.cf.read(self.path)

    def parse(self, database=None):
        if database is None:
            print('please input database name')
        else:
            parseType = self.cf.get(database, 'type')
            if parseType=='mysql':
                value = self.__get_DB(database)
            if parseType=='adhoc':
                value = self.__get_adhoc(database)
            if parseType=='hbase':
                value = self.__get_hbase(database)
            if parseType=='bns':
                value = self.__get_bns(database)
        return value

    def __get_DB(self, database='waimai_anticheat_guard'):
        '''
        返回数据库的信息
        默认读取备库
        '''
        keyList = self.cf.options(database)
        if 'bns' in keyList:
            bns = Bns(self.cf.get(database, 'bns'))
            valueDic = bns.get_random_dic()
            guardInfo = {
                    'host': valueDic['ip'],
                    'port': valueDic['port'],
                    'user': self.cf.get(database, 'user'),
                    'pass': self.cf.get(database, 'pass'),
                    'db': self.cf.get(database, 'db')
                    }
        else:
            guardInfo = {
                    'host': self.cf.get(database, 'host'),
                    'port': self.cf.get(database, 'port'),
                    'user': self.cf.get(database, 'user'),
                    'pass': self.cf.get(database, 'pass'),
                    'db': self.cf.get(database, 'db')
                    }
        return guardInfo

    def __get_adhoc(self, database='ad_hoc_public'):
        '''
        读取adhoc的配置信息
        '''
        adhocDic = {
                'username': self.cf.get(database, 'username'),
                'userpass': self.cf.get(database, 'userpass'),
                'adhoc_url': self.cf.get(database, 'adhoc_url'),
                'getkey_url': self.cf.get(database, 'getkey_url'),
                }
        return adhocDic

    def __get_hbase(self, database='ad_hoc_public'):
        '''
        读取所有hbase的ip
        '''
        itemList = self.cf.items(database)
        return itemList

    def __get_bns(self, database='front_bns'):
        '''
        返回Bns的相关信息
        '''
        bns = Bns.Bns(self.cf.get(database, 'bns'))
        httpString = bns.get_random_info()
        return httpString
