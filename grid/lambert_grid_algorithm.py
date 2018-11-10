# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LambertGrid
                                 A QGIS plugin
 Equal area lambert grid
                              -------------------
        begin                : 2016-11-15
        copyright            : (C) 2016 by GeoHey
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
from __future__ import absolute_import

from builtins import str
__author__ = 'GeoHey'
__date__ = '2016-11-15'
__copyright__ = '(C) 2016 by GeoHey'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os 
from qgis.PyQt.QtCore import QSettings, QVariant
from qgis.core import QgsVectorFileWriter, QgsMessageLog, QgsFeature, QGis, QgsGeometry, QgsPoint, QgsFields, QgsCoordinateReferenceSystem
from qgis.PyQt.QtGui import QIcon

# from processing.tools.system import *
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterNumber, ParameterCrs, ParameterExtent, ParameterSelection
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from .lambert_grid_core import LambertGrid
from . import proj_util


class LambertGridAlgorithm(GeoAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'

    YAXE = 'up'
    YAXE_OPTIONS = ['up', 'down']

    CRS = 'EPSG:4326'

    EXTENT = ''

    LEVEL = 10

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/geohey.png')

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Create equal area lambert grids'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Grid tools'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterExtent(self.EXTENT, self.tr('Grid Extent')))

        self.addParameter(ParameterSelection(self.YAXE, self.tr('Y-direction'), self.YAXE_OPTIONS))
        
        self.addParameter(ParameterNumber(self.LEVEL, self.tr('Grid Level'), 0, 19, 9))

        self.addParameter(ParameterCrs(self.CRS, self.tr('Coordinate System'), self.tr('EPSG:4326')))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER, self.tr('Output Grid')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        extent = str(self.getParameterValue(self.EXTENT))
        flip = self.getParameterValue(self.YAXE)
        level = self.getParameterValue(self.LEVEL)
        crs = str(self.getParameterValue(self.CRS))

        QgsMessageLog.logMessage(extent, 'LambertGrid', QgsMessageLog.INFO)
        QgsMessageLog.logMessage(str(flip), 'LambertGrid', QgsMessageLog.INFO)
        QgsMessageLog.logMessage(str(level), 'LambertGrid', QgsMessageLog.INFO)

        output = self.getOutputValue(self.OUTPUT_LAYER)
        extent_arr = [float(extent.split(',')[0]), float(extent.split(',')[1]), float(extent.split(',')[2]), float(extent.split(',')[3])]
        QgsMessageLog.logMessage('specified extent' + str(extent_arr), 'LambertGrid', QgsMessageLog.INFO)

        if (crs == 'EPSG:4326'):
            QgsMessageLog.logMessage(crs, 'LambertGrid', QgsMessageLog.INFO)
            [xmin, ymin] = proj_util.lonlat2lambert([extent_arr[0], extent_arr[2]])
            [xmax, ymax] = proj_util.lonlat2lambert([extent_arr[1], extent_arr[3]])
        else:
            # opts.srs == 'epsg:3857'
            QgsMessageLog.logMessage(crs, 'LambertGrid', QgsMessageLog.INFO)
            [xmin, ymin] = proj_util.webmercator2lonlat([extent_arr[0], extent_arr[2]])
            [xmax, ymax] = proj_util.webmercator2lonlat([extent_arr[1], extent_arr[3]])
            [xmin, ymin] = proj_util.lonlat2lambert([xmin, ymin])
            [xmax, ymax] = proj_util.lonlat2lambert([xmax, ymax])

        QgsMessageLog.logMessage('specified lambert extent' + str([xmin, ymin, xmax, ymax]), 'LambertGrid', QgsMessageLog.INFO)

        grids = LambertGrid(level, xmin, xmax, ymin, ymax, flip)
        
        total_cnt = grids.total_grids
        cnt = 0
        step = int(total_cnt / 100)
        if step == 0:
            step = 1

        msg = 'total grids %d' % total_cnt
        QgsMessageLog.logMessage(msg, 'LambertGrid', QgsMessageLog.INFO)

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        # provider = vectorLayer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        writer = QgsVectorFileWriter(output, systemEncoding, fields, QGis.WKBPolygon, QgsCoordinateReferenceSystem(crs))

        for k in grids.grid_list:
            ext = grids.grid_list[k]

            # QgsMessageLog.logMessage('processing small grid lambert extent ' + str(ext), 'LambertGrid', QgsMessageLog.INFO)
            # transform coordinates
            if (crs == 'EPSG:4326'):
                [xmin, ymin] = proj_util.lambert2lonlat([ext[0], ext[2]])
                [xmax, ymax] = proj_util.lambert2lonlat([ext[1], ext[3]])
            else:
                # opts.srs == 'epsg:3857'
                [xmin, ymin] = proj_util.lambert2lonlat([ext[0], ext[2]])
                [xmax, ymax] = proj_util.lambert2lonlat([ext[1], ext[3]])
                [xmin, ymin] = proj_util.lonlat2webmercator([xmin, ymin])
                [xmax, ymax] = proj_util.lonlat2webmercator([xmax, ymax])

            # QgsMessageLog.logMessage('processing small grid extent ' + str([xmin, ymin, xmax, ymax]), 'LambertGrid', QgsMessageLog.INFO)

            feat = QgsFeature()

            verts = []
            ring_verts = []
            ring_verts.append(QgsPoint(xmin, ymin))
            ring_verts.append(QgsPoint(xmax, ymin))
            ring_verts.append(QgsPoint(xmax, ymax))
            ring_verts.append(QgsPoint(xmin, ymax))
            ring_verts.append(QgsPoint(xmin, ymin))
            verts.append(ring_verts)

            geom = QgsGeometry.fromPolygon(verts)
            # QgsMessageLog.logMessage('small grid geometry ' + str(geom.asPolygon()), 'LambertGrid', QgsMessageLog.INFO)

            feat.setGeometry(geom)
            feat.setAttributes([str(level) + '_' + k])

            writer.addFeature(feat)

            cnt = cnt + 1
            if (cnt % step == 0):
                progress.setPercentage((float(cnt) / float(total_cnt) * 100))