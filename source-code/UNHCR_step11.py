# -*- coding: utf-8 -*-

import os
from .UNHCR_generalFunctions import GeneralFunctions

from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing

class Step11():
    """This class contains all functions needed to perform step 11."""

    def __init__(self, iface):
        """Constructor."""
        
        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self._setupMap()

    def _setupMap(self):
        """Setup map layers and visibility."""

        self.root = QgsProject.instance().layerTreeRoot()
        allLayers = self.root.layerOrder()
        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]

        for layer in allLayers:
            self.root.findLayer(layer.id()).setItemVisibilityChecked(False)

            if layer.name() == "temp":
                QgsProject.instance().removeMapLayer(layer.id())
        
        self.root.findLayer(lyrOSM).setItemVisibilityChecked(True)

    def changeRisk(self, layer, risk):
        """Change the risk level of features of an area the user selected in the given vector layer

        Args:
            layer (QgsVectorLayer): The vector layer in which the risk level will be changed.
            risk (int): The new risk level to be assigned to the selected features.
        """

        self.layer = layer
        self.risk = risk

        self.root.findLayer(self.layer).setItemVisibilityChecked(True)

        self.selectedArea = QgsVectorLayer('Polygon?crs=' + self.layer.crs().authid(), "temp", 'memory')
        QgsProject.instance().addMapLayer(self.selectedArea)

        # without opening a dialog form
        form_config = self.selectedArea.editFormConfig()
        form_config.setSuppress(QgsEditFormConfig.SuppressOn)
        self.selectedArea.setEditFormConfig(form_config)

        # Connect the layer to the signal featureAdded, so when a feature is
        # added to the layer, the feature_added function is called    
        self.selectedArea.featureAdded.connect(self._feature_added)

        # Set the layer in edit mode
        self.selectedArea.startEditing()
        self.layer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    def _feature_added(self):
        """Function called when a feature is added to the layer."""

        form_config_buildings = self.layer.editFormConfig()
        form_config_buildings.setSuppress(QgsEditFormConfig.SuppressOn)
        self.layer.setEditFormConfig(form_config_buildings)

        #select by location
        processing.run("qgis:selectbylocation", {
                        "INPUT":self.layer,\
                        "PREDICATE":0,\
                        "INTERSECT":self.selectedArea,\
                        "METHOD":0})
        
        drawnArea = next(self.selectedArea.getFeatures(), None)
        drawnGeometry = drawnArea.geometry()

        # Prepare a list to store new features
        new_features = []

        for feature in self.layer.selectedFeatures():
    
            if feature.geometry().intersects(drawnGeometry):

                # Store the original risk level
                original_feature = feature
                
                # Calculate the intersection geometry
                intersection = feature.geometry().intersection(drawnGeometry)

                # Create a new feature for the remaining part
                remaining_geometry = feature.geometry().difference(intersection)

                # Update the geometry of the feature with the intersection
                feature.setGeometry(remaining_geometry)

                if not intersection.isEmpty():
                    new_feature = QgsFeature(self.layer.fields())
                    new_feature.setGeometry(intersection)
                    new_feature.setAttributes(original_feature.attributes())
                    new_feature['SumVul'] = self.risk

                    # Add the new feature to list
                    new_features.append(new_feature)

            # Update the feature in the layer
            self.layer.updateFeature(feature)
            
        # Add new features to the layer
        if new_features:
            self.layer.addFeatures(new_features)

        # Disconnect from the signal
        self.selectedArea.featureAdded.disconnect()
        self.layer.removeSelection()

        # Save changes and end edit mode
        self.selectedArea.commitChanges()
        self.layer.commitChanges()

        root = QgsProject.instance().layerTreeRoot()
        root.findLayer(self.selectedArea).setItemVisibilityChecked(False)

    
