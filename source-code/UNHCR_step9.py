# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing
from .UNHCR_generalFunctions import GeneralFunctions

class Step9():
    """This class contains all functions needed to perform step 9."""

    def __init__(self, iface):
        """Constructor."""
        
        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.roadsClipLayer = self._setupMap()
        
    def _setupMap(self):
        """Setup map layers and visibility."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

        self.generalFunctions.addLayer("Roads_Clip", "LayerStyle_Roads")

        lyrRoadsClip = QgsProject.instance().mapLayersByName("Roads_Clip")[0]
        root.findLayer(lyrRoadsClip).setItemVisibilityChecked(True)
        
        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        #self.generalFunctions.removeLayer("tempbuilding")

        return lyrRoadsClip

    def addInfrastructure(self, type):
        """Enables adding infrastructure.
        
        Args:
            type (str): Infrastructure type.
        """

        self.type = type

        form_config = self.roadsClipLayer.editFormConfig() 
        form_config.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.roadsClipLayer.setEditFormConfig(form_config)

        self.roadsClipLayer.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.roadsClipLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self, fId):
        """Function called when a feature is added to the layer."""

        self.roadsClipLayer.select(fId)

        for f in self.roadsClipLayer.selectedFeatures():
            f['type'] = self.type
            f['assets'] = 'InternalRoadsAndWalkways' #### ????
            self.roadsClipLayer.updateFeature(f)

            # Disconnect from the signal
            self.roadsClipLayer.featureAdded.disconnect()

            # Save changes and end edit mode
            self.roadsClipLayer.commitChanges()
            self.roadsClipLayer.removeSelection()
        