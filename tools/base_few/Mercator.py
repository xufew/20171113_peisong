# =======================
# -*- coding: utf-8 -*-
# author: LONGFEI XU
# Try your best
# ============
import math


_MCBAND = [12890594.86,8362377.87,5591021,3481989.83,1678043.12,0]
_LLBAND = [75,60,45,30,15,0]
_MC2LL = [[1.410526172116255e-008,8.983055096488720e-006,-1.99398338163310,2.009824383106796e+002,-1.872403703815547e+002,91.60875166698430,-23.38765649603339,2.57121317296198,-0.03801003308653,1.733798120000000e+007],[-7.435856389565537e-009,8.983055097726239e-006,-0.78625201886289,96.32687599759846,-1.85204757529826,-59.36935905485877,47.40033549296737,-16.50741931063887,2.28786674699375,1.026014486000000e+007],[-3.030883460898826e-008,8.983055099835780e-006,0.30071316287616,59.74293618442277,7.35798407487100,-25.38371002664745,13.45380521110908,-3.29883767235584,0.32710905363475,6.856817370000000e+006],[-1.981981304930552e-008,8.983055099779535e-006,0.03278182852591,40.31678527705744,0.65659298677277,-4.44255534477492,0.85341911805263,0.12923347998204,-0.04625736007561,4.482777060000000e+006],[3.091913710684370e-009,8.983055096812155e-006,0.00006995724062,23.10934304144901,-0.00023663490511,-0.63218178102420,-0.00663494467273,0.03430082397953,-0.00466043876332,2.555164400000000e+006],[2.890871144776878e-009,8.983055095805407e-006,-0.00000003068298,7.47137025468032,-0.00000353937994,-0.02145144861037,-0.00001234426596,0.00010322952773,-0.00000323890364,8.260885000000000e+005]]
_LL2MC = [[-0.00157021024440, 1.113207020616939e+005, 1.704480524535203e+015, -1.033898737604234e+016, 2.611266785660388e+016,-3.514966917665370e+016,2.659570071840392e+016,-1.072501245418824e+016, 1.800819912950474e+015,82.5], [8.277824516172526e-004,1.113207020463578e+005,6.477955746671608e+008,-4.082003173641316e+009, 1.077490566351142e+010,-1.517187553151559e+010,1.205306533862167e+010,-5.124939663577472e+009, 9.133119359512032e+008,67.5], [0.00337398766765,1.113207020202162e+005,4.481351045890365e+006,-2.339375119931662e+007, 7.968221547186455e+007,-1.159649932797253e+008,9.723671115602145e+007,-4.366194633752821e+007,8.477230501135234e+006,52.5], [0.00220636496208,1.113207020209128e+005,5.175186112841131e+004,3.796837749470245e+006,9.920137397791013e+005, -1.221952217112870e+006,1.340652697009075e+006,-6.209436990984312e+005,1.444169293806241e+005,37.5], [-3.441963504368392e-004,1.113207020576856e+005,2.782353980772752e+002,2.485758690035394e+006,6.070750963243378e+003, 5.482118345352118e+004,9.540606633304236e+003,-2.710553267466450e+003,1.405483844121726e+003,22.5], [-3.218135878613132e-004,1.113207020701615e+005,0.00369383431289,8.237256402795718e+005,0.46104986909093, 2.351343141331292e+003,1.58060784298199,8.77738589078284,0.37238884252424,7.45]]

def convertLL2MC(point):
    '''
    将经纬度坐标转化为墨卡托坐标
    point: 经纬度坐标
    '''
    _point[0] = getLoop(_point[0], -180, 180)
    _point[1] = getRange(_point[1], -74, 74)
    _temp = _point
    _cnt = len(_LLBAND)
    for i in range(0, _cnt):
        if(_temp[1] >= _LLBAND[i]):
            _factor = _LL2MC[i]
            break
    if (len(_factor) == 0):
        for i in range(_cnt - 1, 0, -1):
            if(_temp[1] <= - _LLBAND[i]):
                _factor = _LL2MC[_i]
                break
    _mc = convertor(_point, _factor)
    _fmtMc = [round(_mc[0], 2), round(_mc[1], 2)]
    return _fmtMc

def convertMC2LL(_point):
    '''
    将墨卡托坐标转化为经纬度坐标
    point: 墨卡托坐标
    '''
    _temp = [abs(_point[0]), abs(_point[1])]
    _cnt = len(_MCBAND)
    for i in range(0, _cnt):
        if (_temp[1] >= _MCBAND[i]):
            _factor = _MC2LL[i]
            break
    _arrTemp = convertor(_point, _factor)
    _lng = round(_arrTemp[0], 6)
    _lat = round(_arrTemp[1], 6)

    _ll = [_lng, _lat]
    return _ll

def getDistance(_pointAMM, _pointBMM, _pointALL = []):
    '''
    计算两点之间距离
    pointAMM  基准点墨卡托坐标
    pointBMM  比较点墨卡托坐标
    pointALL  基准点经纬度坐标，默认为null。以此计算纬度
    return  两点距离，单位：米
    '''
    if (len(_pointALL) == 0):
        _pointALL = convertMC2LL(_pointAMM)
    if (_pointALL[1] is None):
        return false
    _distance = math.sqrt(
            math.pow((_pointAMM[0]-_pointBMM[0]), 2) + math.pow((_pointAMM[1]-_pointBMM[1]), 2)
            )
    _distance *= math.cos(math.radians(_pointALL[1]))
    return _distance

def convertor(_fromPoint, _factor):
    if (len(_fromPoint) == 0 or len(_factor) == 0):
      return

    _x = _factor[0] + _factor[1] * abs(_fromPoint[0])
    _temp = abs(_fromPoint[1]) / _factor[9]
    _y = _factor[2] + \
            _factor[3] * _temp + \
            _factor[4] * _temp * _temp + \
            _factor[5] * _temp * _temp * _temp + \
            _factor[6] * _temp * _temp * _temp * _temp + \
            _factor[7] * _temp * _temp * _temp * _temp * _temp + \
            _factor[8] * _temp * _temp * _temp * _temp * _temp * _temp
    _x *= (-1 if _fromPoint[0] < 0 else 1)
    _y *= (-1 if _fromPoint[1] < 0 else 1)
    return [_x, _y]

def getRange(_v, _a, _b):
    if(not _a is  None):
        _v = max(_v, _a)

    if(not _b is None):
        _v = min(_v, _b)
    return _v

def getLoop(_v, _a, _b):
    while(_v > _b):
         _v -= _b - _a
    while(_v < _a):
         _v += _b - _a
    return _v


if __name__ == '__main__':
	print(getDistance([12960343.27, 4848184.29], [12962873.7, 4849687.9]))
