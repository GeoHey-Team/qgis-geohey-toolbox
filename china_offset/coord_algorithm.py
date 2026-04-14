# -*- coding: utf-8 -*-
"""
QGIS 4 Processing algorithms for Chinese coordinate conversion.

Single base class handles all geometry types;
subclasses only define identity + which transform function to call.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    Qgis,
    QgsFeature,
    QgsFeatureSink,
    QgsGeometry,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsWkbTypes,
)

from . import transform


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class _CoordConvertBase(QgsProcessingAlgorithm):
    """
    Abstract base for all six coordinate converters.

    Subclasses must define:
        _NAME        — algorithm id  (e.g. "WGS to GCJ02")
        _DISPLAY     — display name  (e.g. "WGS84 → GCJ02")
        _FUNC        — callable(lon, lat) -> (lon, lat)
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    _NAME: str
    _DISPLAY: str
    _FUNC: staticmethod

    # -- algorithm registration ------------------------------------------

    def name(self):
        return self._NAME

    def displayName(self):
        return self.tr(self._DISPLAY)

    def group(self):
        return self.tr("China Coord Convert")

    def groupId(self):
        return "china_coord_convert"

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return self.__class__()

    # -- parameter definition --------------------------------------------

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorAnyGeometry],
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer"),
            )
        )

    # -- processing ------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise ValueError("Invalid input layer")

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs(),
        )

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        fn = self._FUNC  # the transform function

        for current, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break

            geom = feature.geometry()
            if geom.isNull():
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                feedback.setProgress(int(current * total))
                continue

            new_geom = self._transform_geometry(geom, fn)

            out = QgsFeature()
            out.setAttributes(feature.attributes())
            out.setGeometry(new_geom)
            sink.addFeature(out, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    # -- geometry transform helpers --------------------------------------

    @staticmethod
    def _transform_point(pt, fn):
        """Transform a single QgsPointXY, return QgsPointXY."""
        lon, lat = fn(pt.x(), pt.y())
        return QgsPointXY(lon, lat)

    def _transform_geometry(self, geom, fn):
        """
        Transform any supported geometry type.
        Uses the flat wkbType (strips Z/M/ZM) to dispatch,
        then preserves the original dimensionality.
        """
        flat = QgsWkbTypes.flatType(geom.wkbType())
        tp = self._transform_point

        # -- Point --
        if flat == QgsWkbTypes.Point:
            pt = geom.asPoint()
            return QgsGeometry.fromPointXY(tp(pt, fn))

        # -- LineString --
        if flat == QgsWkbTypes.LineString:
            return QgsGeometry.fromPolylineXY(
                [tp(p, fn) for p in geom.asPolyline()]
            )

        # -- Polygon --
        if flat == QgsWkbTypes.Polygon:
            return QgsGeometry.fromPolygonXY(
                [[tp(p, fn) for p in ring] for ring in geom.asPolygon()]
            )

        # -- MultiPoint --
        if flat == QgsWkbTypes.MultiPoint:
            return QgsGeometry.fromMultiPointXY(
                [tp(p, fn) for p in geom.asMultiPoint()]
            )

        # -- MultiLineString --
        if flat == QgsWkbTypes.MultiLineString:
            return QgsGeometry.fromMultiPolylineXY(
                [[tp(p, fn) for p in part] for part in geom.asMultiPolyline()]
            )

        # -- MultiPolygon --
        if flat == QgsWkbTypes.MultiPolygon:
            return QgsGeometry.fromMultiPolygonXY(
                [
                    [[tp(p, fn) for p in ring] for ring in poly]
                    for poly in geom.asMultiPolygon()
                ]
            )

        # Unsupported type — pass through unchanged
        return geom


# ---------------------------------------------------------------------------
# Concrete algorithms (one-liner each)
# ---------------------------------------------------------------------------

class WGS2GCJ(_CoordConvertBase):
    _NAME = "wgs2gcj"
    _DISPLAY = "WGS84 → GCJ02"
    _FUNC = staticmethod(transform.wgs2gcj)

class GCJ2WGS(_CoordConvertBase):
    _NAME = "gcj2wgs"
    _DISPLAY = "GCJ02 → WGS84"
    _FUNC = staticmethod(transform.gcj2wgs)

class GCJ2BD(_CoordConvertBase):
    _NAME = "gcj2bd"
    _DISPLAY = "GCJ02 → BD09"
    _FUNC = staticmethod(transform.gcj2bd)

class BD2GCJ(_CoordConvertBase):
    _NAME = "bd2gcj"
    _DISPLAY = "BD09 → GCJ02"
    _FUNC = staticmethod(transform.bd2gcj)

class WGS2BD(_CoordConvertBase):
    _NAME = "wgs2bd"
    _DISPLAY = "WGS84 → BD09"
    _FUNC = staticmethod(transform.wgs2bd)

class BD2WGS(_CoordConvertBase):
    _NAME = "bd2wgs"
    _DISPLAY = "BD09 → WGS84"
    _FUNC = staticmethod(transform.bd2wgs)
