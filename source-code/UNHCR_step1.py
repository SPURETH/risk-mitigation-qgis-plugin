# -*- coding: utf-8 -*-

import os
from .UNHCR_generalFunctions import GeneralFunctions
from qgis.core import QgsProject, QgsEditFormConfig, QgsRasterLayer
from qgis.PyQt.QtCore import QSettings


class Step1:
    """This class contains all functions needed to perform step 1."""

    def __init__(self, iface):
        """Constructor for Step1 class.

        Args:
            iface: Reference to the QGIS interface.
        """

        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.campLayer = self._setupMap()

    def _setupMap(self):
        """Setup map layers and visibility."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

        self.generalFunctions.addLayer("SettlementArea", "LayerStyle_SettlementArea")
        lyrCampArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        root.findLayer(lyrCampArea).setItemVisibilityChecked(True)

        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        return lyrCampArea

    def drawCamp(self):
        """Enables drawing a camp area on the map."""

        form_config = self.campLayer.editFormConfig()
        form_config.setSuppress(QgsEditFormConfig.SuppressOn)
        self.campLayer.setEditFormConfig(form_config)

        # Connect the layer to the signal featureAdded, so when a feature is
        # added to the layer, the feature_added function is called
        self.campLayer.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.campLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self):

        # Disconnect from the signal
        self.campLayer.featureAdded.disconnect()

        # Save changes and end edit mode
        self.campLayer.commitChanges()

    def layerNotEmpty(self):
        """Check if the camp layer is not empty.

        Returns:
            bool: True if the layer is not empty, False otherwise.
        """
        
        return self.campLayer.featureCount() != 0

    def deleteCampArea(self):
        """Delete the feature in camp layer."""

        self.campLayer.startEditing()

        for f in self.campLayer.getFeatures():
            self.campLayer.deleteFeature(f.id())

        self.campLayer.commitChanges()
        self.iface.mapCanvas().refresh()

    def addRasterLayer(self, filePath, layername):
        """Add a raster layer.

        Args:
            filePath (str): The path to the raster file.
            layername (str): The name to assign to the layer.

        Returns:
            QgsRasterLayer: The added raster layer.
        """

        return QgsRasterLayer(filePath, layername)
    
    def addGoogleSatelliteLayer (self):

        urlWithParams = 'type=xyz&url=https://www.google.cn/maps/vt?lyrs%3Ds@189%26gl%3Dcn%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0'
        rasterLyr = QgsRasterLayer(urlWithParams, 'Basemap', "wms")
        QgsProject.instance().addMapLayer(rasterLyr)
