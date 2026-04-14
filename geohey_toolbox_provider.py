# -*- coding: utf-8 -*-
"""Processing provider that registers all coordinate-conversion algorithms."""

import os
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .china_offset.coord_algorithm import (
    WGS2GCJ, GCJ2WGS, GCJ2BD, BD2GCJ, WGS2BD, BD2WGS,
)


class GeoHeyToolboxProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        for cls in (WGS2GCJ, GCJ2WGS, GCJ2BD, BD2GCJ, WGS2BD, BD2WGS):
            self.addAlgorithm(cls())

    def id(self):
        return "GeoHey"

    def name(self):
        return "GeoHey"

    def longName(self):
        return "GeoHey 坐标转换工具箱"

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))
