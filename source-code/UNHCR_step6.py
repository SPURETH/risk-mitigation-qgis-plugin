# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing
from .UNHCR_generalFunctions import GeneralFunctions

class Step6():
    """This class contains all functions needed to perform step 6."""

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

        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        self.generalFunctions.addLayer("Buildings_Clip", "LayerStyle_Buildings")

        lyrBuildingClip = QgsProject.instance().mapLayersByName("Buildings_Clip")[0]
        root.findLayer(lyrBuildingClip).setItemVisibilityChecked(True)

        return lyrBuildingClip

    def changeBuilding(self, type, construction):
        """Enables changing type of buildings.
        
        Args:
            type (str): Building type.
            construction (str): Type of construction.
        """

        self.type = type
        self.construction = construction

        self.selectedBuildings = QgsVectorLayer('Polygon?crs=epsg:4326', "temp", 'memory') # tempbuilding
        QgsProject.instance().addMapLayer(self.selectedBuildings)

        # without opening a dialog form
        form_config = self.selectedBuildings.editFormConfig() 
        form_config.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.selectedBuildings.setEditFormConfig(form_config)

        # Connect the layer to the signal featureAdded, so when a feature is
        # added to the layer, the feature_added function is called    
        self.selectedBuildings.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.selectedBuildings.startEditing()
        self.buildingClipLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self):
        """Function called when a feature is added to the layer."""

        form_config_buildings = self.buildingClipLayer.editFormConfig() 
        form_config_buildings.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.buildingClipLayer.setEditFormConfig(form_config_buildings)

        #select by location
        processing.run("qgis:selectbylocation", {
                        "INPUT":self.buildingClipLayer,\
                        "PREDICATE":0,\
                        "INTERSECT":self.selectedBuildings,\
                        "METHOD":0})

        for f in self.buildingClipLayer.selectedFeatures():
            f['assets'] = self.type
            f['type'] = self.construction
            self.buildingClipLayer.updateFeature(f)
            

        # Disconnect from the signal
        self.selectedBuildings.featureAdded.disconnect()
        self.buildingClipLayer.removeSelection()

        # Save changes and end edit mode
        self.selectedBuildings.commitChanges()
        self.buildingClipLayer.commitChanges()

        #self.selectedBuildings.rollBack()

        root = QgsProject.instance().layerTreeRoot()
        root.findLayer(self.selectedBuildings).setItemVisibilityChecked(False)




        