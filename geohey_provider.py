# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GeoHeyProvider
                                 A QGIS plugin
 GeoHey provider info
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
"""

__author__ = 'GeoHey'
__date__ = '2016-10-29'
__copyright__ = '(C) 2016 by GeoHey'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt4.QtGui import *
from processing.tools.system import *

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from china_offset.offset_wgs84_algorithm import OffsetWGS84Algorithm
from grid.lambert_grid_algorithm import LambertGridAlgorithm
from china_offset.wgs2gcj import WGS2GCJ
from china_offset.gcj2wgs import GCJ2WGS
from china_offset.gcj2bd import GCJ2BD
from china_offset.bd2gcj import BD2GCJ
from china_offset.wgs2bd import WGS2BD
from china_offset.bd2wgs import BD2WGS

class GeoHeyProvider(AlgorithmProvider):

    MY_DUMMY_SETTING = 'MY_DUMMY_SETTING'

    def __init__(self):
        AlgorithmProvider.__init__(self)

        # Deactivate provider by default
        self.activate = False

        # Load algorithms
        self.alglist = [WGS2GCJ() , GCJ2WGS(), GCJ2BD(), BD2GCJ(), WGS2BD(), BD2WGS(),  LambertGridAlgorithm()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        """In this method we add settings needed to configure our
        provider.

        Do not forget to call the parent method, since it takes care
        or automatically adding a setting for activating or
        deactivating the algorithms in the provider.
        """
        AlgorithmProvider.initializeSettings(self)
        ProcessingConfig.addSetting(Setting('Example algorithms',
            GeoHeyProvider.MY_DUMMY_SETTING,
            'Example setting', 'Default value'))

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        AlgorithmProvider.unload(self)
        ProcessingConfig.removeSetting(
            GeoHeyProvider.MY_DUMMY_SETTING)

    def getName(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'GeoHey'

    def getDescription(self):
        """This is the provired full name.
        """
        return 'GeoHey Toolbox'

    # def getIcon(self):
    #     """We return the default icon.
    #     """
    #     return AlgorithmProvider.getIcon(self)
    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/geohey.png')

    def _loadAlgorithms(self):
        """Here we fill the list of algorithms in self.algs.

        This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.

        In this case, since the list is always the same, we assign from
        the pre-made list. This assignment has to be done in this method
        even if the list does not change, since the self.algs list is
        cleared before calling this method.
        """
        self.algs = self.alglist
