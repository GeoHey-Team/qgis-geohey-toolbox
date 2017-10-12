# -*- coding: utf-8 -*-

"""
/***************************************************************************
 OffsetWGS84
                                 A QGIS plugin
 offset wgs84 to gcj02 coordinate system
                              -------------------
        begin                : 2016-10-29
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
        modify                : 2017-10-11
        copyright            : (C) 2017 by GeoHey
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

__author__ = 'GeoHey'
__date__ = '2016-10-29'
__copyright__ = '(C) 2016 by GeoHey'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorFileWriter
from qgis.core import *
from PyQt4.QtGui import *

from processing.tools.system import *
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector
from offset_wgs84_core import OffsetWGS84Engine
from transform import bd2gcj


class BD2GCJ(GeoAlgorithm):
    """This is an algorithm that takes a wgs84 coordinate vector layer, 
    and create a new vector layer which is gcj02 coordinate system 
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/geohey.png')

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'BaiDu to GCJ02'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'China Coord Convert'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER,
            self.tr('Input layer'), [ParameterVector.VECTOR_TYPE_ANY], False))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
            self.tr('Offseted layer')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        output = self.getOutputValue(self.OUTPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        vectorLayer = dataobjects.getObjectFromUri(inputFilename)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        provider = vectorLayer.dataProvider()
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        writer = QgsVectorFileWriter(output, systemEncoding, provider.fields(), provider.geometryType(), provider.crs())

        # Do the transform
        QgsMessageLog.logMessage("Start processing ...", 'WGS2GCJ', QgsMessageLog.INFO)

        # engine = OffsetWGS84Engine()
        features = vector.features(vectorLayer)
        total_cnt = len(features)
        cnt = 0
        step = int(total_cnt / 100)
        if step == 0:
            step = 1
            
        for f in features:
            attrs = f.attributes()
            geom = f.geometry()
            geom_type = geom.wkbType()

            new_f = QgsFeature()
            if geom_type == QGis.WKBPoint:
                vertices = geom.asPoint()
                new_vert = bd2gcj(vertices[0], vertices[1])
                new_f.setGeometry(QgsGeometry.fromPoint(QgsPoint(new_vert[0], new_vert[1])))
            elif geom_type == QGis.WKBMultiPoint:
                vertices = geom.asMultiPoint()
                new_vert = []
                for pt in vertices:
                    new_pt = bd2gcj(pt[0], pt[1])
                    new_vert.append(QgsPoint(new_pt[0], new_pt[1]))
                new_f.setGeometry(QgsGeometry.fromMultiPoint(new_vert))
            elif geom_type == QGis.WKBLineString:
                vertices = geom.asPolyline()

                new_vert = []
                for pt in vertices:
                    new_pt = bd2gcj(pt[0], pt[1])
                    new_vert.append(QgsPoint(new_pt[0], new_pt[1]))
                new_f.setGeometry(QgsGeometry.fromPolyline(new_vert))
            elif geom_type == QGis.WKBMultiLineString:
                vertices = geom.asMultiPolyline()
                new_vert = []
                for part in vertices:
                    linestring = []
                    for pt in part:
                        new_pt = bd2gcj(pt[0], pt[1])
                        linestring.append(QgsPoint(new_pt[0], new_pt[1]))
                    new_vert.append(linestring)
                new_f.setGeometry(QgsGeometry.fromMultiPolyline(new_vert))
            elif geom_type == QGis.WKBPolygon:
                vertices = geom.asPolygon()
                new_vert = []
                for ring in vertices:
                    ring_vert = []
                    for pt in ring:
                        new_pt = bd2gcj(pt[0], pt[1])
                        ring_vert.append(QgsPoint(new_pt[0], new_pt[1]))
                    new_vert.append(ring_vert)
                new_f.setGeometry(QgsGeometry.fromPolygon(new_vert))
            elif geom_type == QGis.WKBMultiPolygon:
                vertices = geom.asMultiPolygon()
                new_vert = []
                for part in vertices:
                    ply = []
                    for ring in part:
                        ring_vert = []
                        for pt in ring:
                            new_pt = bd2gcj(pt[0], pt[1])
                            ring_vert.append(QgsPoint(new_pt[0], new_pt[1]))
                        ply.append(ring_vert)
                    new_vert.append(ply)
                new_f.setGeometry(QgsGeometry.fromMultiPolygon(new_vert))
            else:
                continue
            
            new_f.setAttributes(attrs)
            writer.addFeature(new_f)
            cnt = cnt + 1
            if (cnt % step == 0):
                progress.setPercentage((float(cnt) / float(total_cnt) * 100))
        QgsMessageLog.logMessage("Successful finished.", 'BD2GCJ', QgsMessageLog.INFO)