# -*- coding: utf-8 -*-
"""Plugin entry point — registers the Processing provider."""

from qgis.core import QgsApplication
from .geohey_toolbox_provider import GeoHeyToolboxProvider


class GeoHeyToolboxPlugin:

    def __init__(self):
        self.provider = None

    def initGui(self):
        self.provider = GeoHeyToolboxProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
