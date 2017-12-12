# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============


class Stringer():
    '''
    处理字符串的操作
    strip_string(string),去除可能导致分列和换行错误
    replace(text, {}),替换所有要替换字段
    '''
    def __init__(self):
        pass

    def strip_string(self, thisString):
        '''
        strip_string(string)
        '''
        replaceDic = {
                '\t': ';',
                '\n': ';',
                '\r': ';',
                '\r\n': ';'
                }
        outString = self.replace(thisString, replaceDic)
        outString = outString.strip()
        return outString

    def replace(self, text, replaceDic):
        '''
        replace(text, replaceDic)
        replaceDic:{'1':'3', '4':'5'}, 替换掉text里面所有对应
        '''
        text = "".join([replaceDic.get(c, c) for c in text])
        return text
