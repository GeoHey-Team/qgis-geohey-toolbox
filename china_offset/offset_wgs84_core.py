# -*- coding: utf-8 -*-
##########################################################################################
"""
/***************************************************************************
 OffsetWGS84Core
                                 A QGIS plugin
 Class with methods for geometry and attributes processing
                              -------------------
        begin                : 2016-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Atlas Xu
        email                : xux@geohey.com
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
##########################################################################################
import math
from math import sin, cos, sqrt, fabs
from math import pi as PI




# Class for Offset WGS84:
class OffsetWGS84Engine(object):
    def __init__(self):
        self.a = 6378245.0
        self.f = 1 / 298.3
        self.b = self.a * (1 - self.f)
        self.ee = 1 - (self.b * self.b) / (self.a * self.a)
    
    
    def isInChina(self, lon, lat):
        if (lon >= 72.004 and lon <= 137.8347 and lat >= 0.8293 and lat <= 55.8271):
            return True
        else:
            return False
        
    
    def wgs84ToGcj02(self, coord):
        lon = coord[0]
        lat = coord[1]
        
        if not self.isInChina(lon, lat):
            return [lon, lat]

        dLon = self.lonToGcj02(lon - 105.0, lat - 35.0)
        dLat = self.latToGcj02(lon - 105.0, lat - 35.0)
        
        radLat = lat / 180.0 * math.pi
        magic = math.sin(radLat)
        magic = 1 - self.ee * magic * magic
        sqrtMagic = math.sqrt(magic)
        dLon = (dLon * 180.0) / (self.a / sqrtMagic * math.cos(radLat) * math.pi)
        dLat = (dLat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtMagic) * math.pi)
        
        lon_out = lon + dLon
        lat_out = lat + dLat

        return [lon_out, lat_out]
        
        
    def lonToGcj02(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret
        
        
    def latToGcj02(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret


# =================================================sshuair=============================================================
# define ellipsoid
a = 6378245.0
f = 1 / 298.3
b = a * (1 - f)
ee = 1 - (b * b) / (a * a)

# check if the point in china
def outOfChina(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)

def geohey_transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (160.0 * sin(y / 12.0 * PI) + 320.0 * sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret

def geohey_transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x +  0.1 * x * y + 0.1 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x * PI / 30.0)) * 2.0 / 3.0
    return ret


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
    w1 = tuple(map(lambda x: x[0]-(x[1]-x[2]), zip(w0,g1,g0)))
    # delta = w1 - w0
    delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
    while (abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6):
        w0 = w1
        g1 = wgs2gcj(w0[0], w0[1])
        # w1 = w0 - (g1 - g0)
        w1 = tuple(map(lambda x: x[0]-(x[1]-x[2]), zip(w0,g1,g0)))
        # delta = w1 - w0
        delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
    return w1


class GCJ2WGS(object):
    def __init__(self):
        self.ee = ee
    
    def gcj2wgs(self, coord):
        pass
        # CREATE OR REPLACE FUNCTION geohey_gcj2wgs(gcjLon double precision, gcjLat double precision)
        #     RETURNS point
        # AS $$
        # DECLARE
        #     g0 point;
        #     w0 point;
        #     g1 point;
        #     w1 point;
        #     delta point;
        # BEGIN
        # g0 := point(gcjLon, gcjLat);
        # w0 := g0;
        # g1 := geohey_wgs2gcj(w0[0], w0[1]);
        # w1 := w0 - (g1 - g0);
        # delta := w1 - w0;
        # WHILE (abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6) LOOP
        #     w0 := w1;
        #     g1 := geohey_wgs2gcj(w0[0], w0[1]);
        #     w1 := w0 - (g1 - g0);
        #     delta := w1 - w0;
        # end LOOP;
        # return w1;
        # END;
        # $$ LANGUAGE plpgsql;



if __name__ == '__main__':
    # wgs2gcj
    # coord = (112, 40)
    # trans = WGS2GCJ()
    print(wgs2gcj(112, 40))
    print(gcj2wgs(112.00678230985764, 40.00112245823686))

    # gcj2wgs