# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import urllib.request
import urllib.parse
import json


class HttpQuery:
    '''
    进行http的访问
    '''
    def __init__(self, proxy=1):
        if proxy==1:
            # 加代理可以走外网
            proxy = urllib.request.ProxyHandler(
                    {
                        'http':'100.64.1.124:8080',
                        'https':'100.64.1.124:8080',
                        }
                    )
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)


    def send_query(self, url, timeout=15, data={}):
        if len(data) == 0:
            req = urllib.request.Request(url)
            result = urllib.request.urlopen(req, timeout=timeout).read()
        else:
            data = urllib.parse.urlencode(data)
            req = urllib.request.Request('%s?%s'%(url, data))
            result = urllib.request.urlopen(req, timeout=timeout).read()
        try:
            dataJson = json.loads(result.decode('utf8'))
        except:
            return data
        return dataJson

    def post_query(self, url, jsonData, timeout=15):
        jsonData = jsonData.encode('utf8')
        request = urllib.request.Request(url)
        request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        result = urllib.request.urlopen(request, jsonData).read()
        try:
            dataJson = json.loads(result.decode('utf8'))
        except:
            return data
        return dataJson
