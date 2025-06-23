# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing
from .UNHCR_generalFunctions import GeneralFunctions

class Step7():
    """This class contains all functions needed to perform step 7."""

    def __init__(self, iface):
        """Constructor."""
        
        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.buildingClipLayer = self._setupMap()
        

    def _setupMap(self):
        """Setup map layers and visibility."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

            if layer.name() == "temp":
                QgsProject.instance().removeMapLayer(layer.id())

        self.generalFunctions.addLayer("Buildings_Clip", "LayerStyle_Buildings")

        lyrBuildingClip = QgsProject.instance().mapLayersByName("Buildings_Clip")[0]
        root.findLayer(lyrBuildingClip).setItemVisibilityChecked(True)

        lyrOSM = QgsProject.instance().mapLayersByName("GBasemap")[0]        
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        return lyrBuildingClip

    def addBuilding(self, type, construction):
        """Enables adding buildings.
        
        Args:
            type (str): Building type.
            construction (str): Type of construction.
        """

        self.type = type
        self.construction = construction

        form_config = self.buildingClipLayer.editFormConfig() 
        form_config.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.buildingClipLayer.setEditFormConfig(form_config)

        self.buildingClipLayer.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.buildingClipLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self, fId):
        """Function called when a feature is added to the layer."""

        self.buildingClipLayer.select(fId)

        for f in self.buildingClipLayer.selectedFeatures():
            f['assets'] = self.type
            f['type'] = self.construction
            self.buildingClipLayer.updateFeature(f)

        # Disconnect from the signal
            self.buildingClipLayer.featureAdded.disconnect()

        # Save changes and end edit mode
            self.buildingClipLayer.commitChanges()
            self.buildingClipLayer.removeSelection()
        