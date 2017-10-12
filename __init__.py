# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoHey-Toolbox
                                 A QGIS plugin
GeoHey toolbox for QGIS
                              -------------------
        begin                : 2016-10-29
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'GeoHey'
__date__ = '2016-10-29'
__copyright__ = '(C) 2016 by GeoHey'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OffsetWGS84 class from file OffsetWGS84.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geohey_toolbox import GeoHeyPlugin
    return GeoHeyPlugin()
