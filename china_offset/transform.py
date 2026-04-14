# -*- coding: utf-8 -*-
"""
Core coordinate-transformation functions.

Supported systems:
  WGS84  — GPS / international standard
  GCJ02  — "火星坐标", Chinese national offset
  BD09   — Baidu further offset on top of GCJ02

Every public function signature:  (lon, lat) -> (lon, lat)
"""

import math
from math import sin, cos, sqrt, fabs, atan2, pi as PI

# --- WGS-84 ellipsoid constants (Krasovsky 1940 used by GCJ02) ---
_a = 6378245.0
_f = 1.0 / 298.3
_b = _a * (1.0 - _f)
_ee = 1.0 - (_b * _b) / (_a * _a)


def _out_of_china(lng: float, lat: float) -> bool:
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def _transform_lat(x: float, y: float) -> float:
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(fabs(x))
    ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * sin(y / 12.0 * PI) + 320.0 * sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lon(x: float, y: float) -> float:
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(fabs(x))
    ret += (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x * PI / 30.0)) * 2.0 / 3.0
    return ret


# ---- WGS84 <-> GCJ02 ----

def wgs2gcj(lon: float, lat: float) -> tuple[float, float]:
    if _out_of_china(lon, lat):
        return lon, lat
    d_lat = _transform_lat(lon - 105.0, lat - 35.0)
    d_lon = _transform_lon(lon - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1.0 - _ee * magic * magic
    sqrt_magic = sqrt(magic)
    d_lat = (d_lat * 180.0) / ((_a * (1.0 - _ee)) / (magic * sqrt_magic) * PI)
    d_lon = (d_lon * 180.0) / (_a / sqrt_magic * cos(rad_lat) * PI)
    return lon + d_lon, lat + d_lat


def gcj2wgs(lon: float, lat: float) -> tuple[float, float]:
    """Iterative approximation — precision ~0.1 m."""
    g0 = (lon, lat)
    w0 = g0
    g1 = wgs2gcj(w0[0], w0[1])
    w1 = (w0[0] - (g1[0] - g0[0]), w0[1] - (g1[1] - g0[1]))
    delta = (w1[0] - w0[0], w1[1] - w0[1])
    while abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6:
        w0 = w1
        g1 = wgs2gcj(w0[0], w0[1])
        w1 = (w0[0] - (g1[0] - g0[0]), w0[1] - (g1[1] - g0[1]))
        delta = (w1[0] - w0[0], w1[1] - w0[1])
    return w1


# ---- GCJ02 <-> BD09 ----

def gcj2bd(lon: float, lat: float) -> tuple[float, float]:
    z = sqrt(lon * lon + lat * lat) + 0.00002 * sin(lat * PI * 3000.0 / 180.0)
    theta = atan2(lat, lon) + 0.000003 * cos(lon * PI * 3000.0 / 180.0)
    return z * cos(theta) + 0.0065, z * sin(theta) + 0.006


def bd2gcj(lon: float, lat: float) -> tuple[float, float]:
    x = lon - 0.0065
    y = lat - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * PI * 3000.0 / 180.0)
    theta = atan2(y, x) - 0.000003 * cos(x * PI * 3000.0 / 180.0)
    return z * cos(theta), z * sin(theta)


# ---- WGS84 <-> BD09 (chained) ----

def wgs2bd(lon: float, lat: float) -> tuple[float, float]:
    gcj = wgs2gcj(lon, lat)
    return gcj2bd(gcj[0], gcj[1])


def bd2wgs(lon: float, lat: float) -> tuple[float, float]:
    gcj = bd2gcj(lon, lat)
    return gcj2wgs(gcj[0], gcj[1])
