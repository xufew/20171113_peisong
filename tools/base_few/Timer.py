# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import time
import datetime


class Timer:
    '''
    add('20170101', year=...), 可对日期做从年到秒的加减
    trans_date_D('20170101', format='%Y%m%d'),string转datetime
    trans_date_S(datetime, format='%Y%m%d'),datetime转string
    trans_orderid_to_date(orderid, format='%Y%m%d'),orderid转string
    get_datelist_start_to_end('20170101', '20170201'),获取此段时间内所有时间
    get_end_day('20170101', format='%Y%m%d'),获取所在月份最后一天
    trans_unix_to_string(unix, format),转unix时间戳到string
    trans_string_to_unix('20170101', format),转string到时间戳
    get_unix_now(),获取当前时间时间戳
    '''
    def __init__(self):
        pass

    def add(
            self,
            date,
            format='%Y%m%d',
            year=0,
            month=0,
            days=0,
            hours=0,
            minutes=0,
            seconds=0
            ):
        '''
        对string的日期做加减操作,输入可以为string也可以为datetime
        输出为datetime的形式
        '''
        if type(date)==type(''):
            dateD = self.trans_date_D(date, format)
        else:
            dateD = date
        if seconds!=0:
            dateD = dateD+datetime.timedelta(seconds=seconds)
        if minutes!=0:
            dateD = dateD+datetime.timedelta(minutes=minutes)
        if hours!=0:
            dateD = dateD+datetime.timedelta(hours=hours)
        if days!=0:
            dateD = dateD+datetime.timedelta(days=days)
        yearNum = 0
        if month!=0:
            inputMonth = dateD.month
            outMonth = inputMonth+month
            if (outMonth>=1) and (outMonth<=12):
                dateD = dateD.replace(month=outMonth)
            elif outMonth>12:
                yearNum = outMonth/12
                acMonth = outMonth-yearNum*12
                dateD = dateD.replace(month=acMonth)
            elif outMonth<1:
                yearNum = -((-outMonth)/12)-1
                acMonth = outMonth-(yearNum)*12
                dateD = dateD.replace(month=acMonth)
        useYear = dateD.year+yearNum
        dateD = dateD.replace(year=useYear)
        if year!=0:
            useYear = dateD.year+year
            dateD = dateD.replace(year=useYear)
        return dateD

    def trans_orderid_to_date(
            self,
            orderID,
            format='%Y%m%d %H:%M:%S'
            ):
        '''
        将orderID转为时间，时间格式为%Y%m%d %H:%M:%S
        '''
        timestamp = float(orderID[:-4])
        timeArray = time.localtime(timestamp)
        stringTime = time.strftime(format, timeArray)
        return stringTime

    def trans_date_D(self, date, format='%Y%m%d'):
        '''
        将string的日期时间转为datetime的形式
        '''
        dateD = datetime.datetime.strptime(date, format)
        return dateD

    def trans_date_S(self, dateD, format='%Y%m%d'):
        '''
        将datetime形式的日期转为string
        '''
        date = datetime.datetime.strftime(dateD, format)
        return date

    def get_datelist_start_to_end(
            self,
            startDate,
            endDate,
            num=10000
            ):
        '''
        获取从开始到结束，之间所有的日期list
        结果为[20170430,20170429,20170428......]
        '''
        startDateD = self.trans_date_D(startDate)
        endDateD = self.trans_date_D(endDate)
        dayNum = (endDateD-startDateD).days
        addStart = True
        if num < dayNum:
            dayNum = num
            addStart = False
        dateList = []
        for i in range(dayNum):
            thisDateD = endDateD-datetime.timedelta(i)
            dateList.append(self.trans_date_S(thisDateD))
        if addStart:
            dateList.append(startDate)
        return dateList

    def get_end_day(self, dateS, format='%Y%m%d'):
        '''
        获取日期所在月份的最后一天
        '''
        dateD = self.trans_date_D(dateS)
        firstDayD = dateD.replace(day=1)
        firstDayD = self.add(firstDayD, month=1)
        lastEnd = firstDayD-datetime.timedelta(days=1)
        lastEndS = self.trans_date_S(lastEnd, format)
        return lastEndS

    def trans_unix_to_string(self, unixFloat, format='%Y%m%d-%H:%M:%S'):
        '''
        将unix时间戳转为给定string形式
        '''
        if type(unixFloat)!=type(0.0):
            unixFloat = float(unixFloat)
        time = datetime.datetime.fromtimestamp(unixFloat)
        timeString = self.trans_date_S(time, format)
        return timeString

    def trans_string_to_unix(self, timeString, format='%Y%m%d-%H:%M:%S'):
        '''
        将string形式的时间转为unix时间戳
        '''
        timeD = self.trans_date_D(timeString, format)
        unixTime = time.mktime(timeD.timetuple())
        return unixTime

    def get_unix_now(self):
        '''
        获取当前unix时间戳
        '''
        dtime = datetime.datetime.now()
        unixNow = time.mktime(dtime.timetuple())
        return unixNow

    def get_time_now(self, format='%Y%m%d-%H:%M:%S'):
        '''
        获取当前时间
        '''
        dtime = datetime.datetime.now()
        dateS = self.trans_date_S(dtime, format)
        return dateS
