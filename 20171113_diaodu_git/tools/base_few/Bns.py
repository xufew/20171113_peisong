# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import random
import subprocess


class Bns:
    '''
    走百度内部bns时调用接口时使用
    使用方法：
    bns = Bns(name)
    httpString = bns.get_random_info()
    每次bns调用get_random_info()都会从所有信息中随机生成一个
    '''
    def __init__(
            self,
            bnsName,
            type='ip'
            ):
        self.bnsName = bnsName
        self.type = type
        self.ipList = []
        # 初始化获取ip等信息
        self._get_info_by_name()

    def _get_info_by_name(self):
        '''
        根据bns的名称，返回所有有用信息
        默认为返回形式为ip，即返回ip端口等信息
        '''
        runSh = 'get_instance_by_service -a {}'.format(
                self.bnsName
                )
        shValue = subprocess.getoutput(runSh)
        infoList = shValue.split('\n')
        if self.type == 'ip':
            # 不同形式，只要在这里另写对每行的处理就好了
            useList = map(
                    lambda x: self.__process_info_line(x),
                    infoList
                    )
        outList = []
        for thisDic in useList:
            if len(thisDic) != 0:
                outList.append(thisDic)
        self.ipList = outList
        return outList

    def __process_info_line(self, stringLine):
        '''
        获取ip和端口的，用于发http请求
        '''
        stringList = stringLine.strip().split(' ')
        if len(stringList) < 6:
            # 去除特殊节点
            return {}
        if stringList[4]=='-1':
            # 已经被删除的节点
            return {}
        name = stringList[2]
        if 'mirror' in name:
            # 过滤掉多有的mirror机器
            return {}
        key = stringList[0]
        ip = stringList[1]
        port = stringList[3]
        valueDic = {
                'key': key,
                'ip': ip,
                'name': name,
                'port': port
                }
        return valueDic

    def get_random_info(self):
        '''
        此方法随机选择一个信息使用，对外开放接口
        返回形式http://10.19.149.192:6006
        '''
        ipNum = len(self.ipList)
        useNum = random.randint(0, ipNum-1)
        if self.type == 'ip':
            useDic = self.ipList[useNum]
            httpString = 'http://{}:{}'.format(
                    useDic['ip'],
                    useDic['port'],
                    )
            return httpString

    def get_random_dic(self):
        '''
        此方法随机选择一个信息使用，对外开放接口
        返回形式
        {
            'ip': 10.19.149.192,
            'port': 6006,
            'name': xxxx,
            'key': xxxx
            }
        '''
        ipNum = len(self.ipList)
        useNum = random.randint(0, ipNum-1)
        if self.type == 'ip':
            useDic = self.ipList[useNum]
            return useDic


if __name__ == '__main__':
    testName = 'group.waimai-frontend.iwaimai.all'
    bns = Bns(testName)
    httpString = bns.get_random_info()
    print(httpString)
