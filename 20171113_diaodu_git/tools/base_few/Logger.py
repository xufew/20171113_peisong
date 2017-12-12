# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import os
import logging


class Logger():
    '''
    初始化日志打印，打印时
    logger = Logger().get_logger()
    logger.info('xxx')
    logger.warning('xxx')
    logger.debug('xxx')
    logger.error('xxx')
    '''
    def __init__(self, path='logger.log', abPath=''):
        '''
        如果输入了abPath，则路径为abPath，否则，运行
        路径的+path之后的绝对路径
        '''
        # 获取路径
        if len(abPath)!=0:
            self.path = abPath
        else:
            self.path = self._get_log_path(path)
        self.logger = self.initial_logger('thisLog', self.path)

    def _get_log_path(self, logPath):
        filePath = os.path.abspath('')
        logPath = '{}/{}'.format(filePath, logPath)
        return logPath

    def initial_logger(self, logName, outPath):
        '''
        初始化日志打印
        '''
        logger = logging.Logger(logName)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(outPath)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
                '%(asctime)s-%(funcName)s-%(levelname)s-%(message)s'
                )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def get_logger(self):
        '''
        获取日志对象
        '''
        return self.logger
