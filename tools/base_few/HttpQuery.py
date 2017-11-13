# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import urllib.request
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

    def send_query(self, url, timeout=15):
        req = urllib.request.Request(url)
        data = urllib.request.urlopen(req, timeout=timeout).read()
        try:
            dataJson = json.loads(data)
        except:
            return data
        return dataJson
