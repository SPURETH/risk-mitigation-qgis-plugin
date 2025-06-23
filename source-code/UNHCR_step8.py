# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing
from .UNHCR_generalFunctions import GeneralFunctions

class Step8():
    """This class contains all functions needed to perform step 8."""

    def __init__(self, iface):
        """Constructor."""
        
        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.infrastructureClipLayer = self._setupMap()
        

    def _setupMap(self):
        """Setup map layers and visibility."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

        self.generalFunctions.addLayer("TechnicalInfrastructure_Clip", "LayerStyle_TechnicalInfrastructure")

        lyrTechnicalClip = QgsProject.instance().mapLayersByName("TechnicalInfrastructure_Clip")[0]
        root.findLayer(lyrTechnicalClip).setItemVisibilityChecked(True)

        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        return lyrTechnicalClip

    def addInfrastrucutre(self, type):
        """Enables adding infrastructure.
        
        Args:
            type (str): Infrastructure type.
        """

        self.type = type

        form_config = self.infrastructureClipLayer.editFormConfig() 
        form_config.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.infrastructureClipLayer.setEditFormConfig(form_config)

        self.infrastructureClipLayer.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.infrastructureClipLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self, fId):
        """Function called when a feature is added to the layer."""

        self.infrastructureClipLayer.select(fId)

        for f in self.infrastructureClipLayer.selectedFeatures():
            f['assets'] = self.type
            self.infrastructureClipLayer.updateFeature(f)

        # Disconnect from the signal
            self.infrastructureClipLayer.featureAdded.disconnect()

        # Save changes and end edit mode
            self.infrastructureClipLayer.commitChanges()
            self.infrastructureClipLayer.removeSelection()
        