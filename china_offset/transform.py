# -*- coding: utf-8 -*-
##########################################################################################
"""
/***************************************************************************
 OffsetWGS84Core
                                 A QGIS plugin
 Class with methods for geometry and attributes processing
                              -------------------
        begin                : 2016-10-11
        git sha              : $Format:%H$
        copyright            : (C) 2017 by sshuair
        email                : sshuair@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
##########################################################################################
from builtins import zip
import math
from math import sin, cos, sqrt, fabs, atan2
from math import pi as PI
# from numba import jit


# =================================================sshuair=============================================================
# define ellipsoid
a = 6378245.0
f = 1 / 298.3
b = a * (1 - f)
ee = 1 - (b * b) / (a * a)

# check if the point in china
def outOfChina(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)

# @jit
def geohey_transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (160.0 * sin(y / 12.0 * PI) + 320.0 * sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret

# @jit
def geohey_transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x +  0.1 * x * y + 0.1 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x * PI / 30.0)) * 2.0 / 3.0
    return ret

# @jit
def wgs2gcj(wgsLon, wgsLat):
    if outOfChina(wgsLon, wgsLat):
        return wgsLon, wgsLat
    dLat = geohey_transformLat(wgsLon - 105.0, wgsLat - 35.0)
    dLon = geohey_transformLon(wgsLon - 105.0, wgsLat - 35.0)
    radLat = wgsLat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * cos(radLat) * PI)
    gcjLat = wgsLat + dLat
    gcjLon = wgsLon + dLon
    return (gcjLon, gcjLat)


def gcj2wgs(gcjLon, gcjLat):
    g0 = (gcjLon, gcjLat)
    w0 = g0
    g1 = wgs2gcj(w0[0], w0[1])
    # w1 = w0 - (g1 - g0)
    w1 = tuple([x[0]-(x[1]-x[2]) for x in zip(w0,g1,g0)])
    # delta = w1 - w0
    delta = tuple([x[0] - x[1] for x in zip(w1, w0)])
    while (abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6):
        w0 = w1
        g1 = wgs2gcj(w0[0], w0[1])
        # w1 = w0 - (g1 - g0)
        w1 = tuple([x[0]-(x[1]-x[2]) for x in zip(w0,g1,g0)])
        # delta = w1 - w0
        delta = tuple([x[0] - x[1] for x in zip(w1, w0)])
    return w1


def gcj2bd(gcjLon, gcjLat):
    z = sqrt(gcjLon * gcjLon + gcjLat * gcjLat) + 0.00002 * sin(gcjLat * PI * 3000.0 / 180.0)
    theta = atan2(gcjLat, gcjLon) + 0.000003 * cos(gcjLon * PI * 3000.0 / 180.0)
    bdLon = z * cos(theta) + 0.0065
    bdLat = z * sin(theta) + 0.006
    return (bdLon, bdLat)


def bd2gcj(bdLon, bdLat):
    x = bdLon - 0.0065
    y = bdLat - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * PI * 3000.0 / 180.0)
    theta = atan2(y, x) - 0.000003 * cos(x * PI * 3000.0 / 180.0)
    gcjLon = z * cos(theta)
    gcjLat = z * sin(theta)
    return (gcjLon, gcjLat)


def wgs2bd(wgsLon, wgsLat):
    gcj = wgs2gcj(wgsLon, wgsLat)
    return gcj2bd(gcj[0], gcj[1])


def bd2wgs(bdLon, bdLat):
    gcj = bd2gcj(bdLon, bdLat)
    return gcj2wgs(gcj[0], gcj[1])


if __name__ == '__main__':
    # wgs2gcj
    # coord = (112, 40)
    # trans = WGS2GCJ()
    print(wgs2gcj(112, 40))
    print(gcj2wgs(112.00678230985764, 40.00112245823686))

    # gcj2wgs