import math

earth_radius = 6378137.0
radians_per_degree = math.pi / 180.0
degrees_per_radian = 180.0 / math.pi
mercator_boundary = 20037508.342787

def lonlat2lambert(pt):
    lon = pt[0]
    lat = pt[1]
    if lon > 180:
        lon = lon - 180

    x = lon
    y = math.sin(lat* radians_per_degree)

    return [x, y]


def lambert2lonlat(pt):
    x = pt[0]
    y = pt[1]
    lon = x
    lat = math.asin(y) / radians_per_degree

    return [lon, lat]


def lonlat2mercator(pt):
    lon = pt[0]
    if lon > 180:
        lon = lon - 180

    lat = pt[1]
    x = lon * mercator_boundary / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / radians_per_degree
    y = y * mercator_boundary / 180

    return [x, y]

def mercator2lonlat(pt):
    lon = pt[0] / mercator_boundary * 180
    lat = pt[1] / mercator_boundary * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * radians_per_degree)) - math.pi / 2)
    
    return [lon, lat]

# the same as lonlat2mercator
def lonlat2webmercator(ll):
    xy = [
        earth_radius * ll[0] * radians_per_degree,
        earth_radius * math.log(math.tan((math.pi * 0.25) + (0.5 * ll[1] * radians_per_degree)))
    ]

    if xy[0] > mercator_boundary:
        xy[0] = mercator_boundary
    if xy[0] < -mercator_boundary:
        xy[0] = -mercator_boundary

    if xy[1] > mercator_boundary:
        xy[1] = mercator_boundary
    if xy[1] < -mercator_boundary:
        xy[1] = -mercator_boundary
    return xy


# the same to mercator2lonlat
def webmercator2lonlat(xy):
    return [
        (xy[0] * degrees_per_radian / earth_radius),
        ((math.pi * 0.5) - 2.0 * math.atan(math.exp(-xy[1] / earth_radius))) * degrees_per_radian
    ]