# -*- coding: utf-8 -*-

import os
from .UNHCR_generalFunctions import GeneralFunctions
from qgis.core import QgsProject, QgsEditFormConfig
from qgis.core import *
from qgis import processing

class Step4():
    """This class contains all functions needed to perform step 4."""

    def __init__(self, iface):
        """Constructor."""
        
        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.floodLayer = self._setupMap()

    def _setupMap(self):
        """Setup map layers and visibility."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

            if layer.name() == "temp":
                QgsProject.instance().removeMapLayer(layer.id())
        
        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]
        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        self.generalFunctions.addLayer("PluvialFlood", "LayerStyle_Flood")
        lyrriverine = QgsProject.instance().mapLayersByName("PluvialFlood")[0]
        root.findLayer(lyrriverine).setItemVisibilityChecked(True)

        self.generalFunctions.addLayer("SettlementArea", "LayerStyle_SettlementArea")
        lyrCampArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        root.findLayer(lyrCampArea).setItemVisibilityChecked(True)

        return lyrriverine

    def adjustFlood(self, intensity):
        """Enables adjusting flood features.
        
        Args:
            returnPeriod (int): Value for return period.
            intensity (int): Value for intensity.
        """

        self.intensity = intensity

        self.selectedArea = QgsVectorLayer('Polygon?crs=' + self.floodLayer.crs().authid(), "temp", 'memory')
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
        self.floodLayer.startEditing()

        # Activate the QGIS add feature tool
        self.iface.actionAddFeature().trigger()

    # Define a function called when a feature is added to the layer
    def _feature_added(self):
        """Function called when a feature is added to the layer."""

        form_config_buildings = self.floodLayer.editFormConfig() 
        form_config_buildings.setSuppress(QgsEditFormConfig.SuppressOn) 
        self.floodLayer.setEditFormConfig(form_config_buildings)

        #select by location
        processing.run("qgis:selectbylocation", {
                        "INPUT":self.floodLayer,\
                        "PREDICATE":0,\
                        "INTERSECT":self.selectedArea,\
                        "METHOD":0})
        

        drawnArea = next(self.selectedArea.getFeatures(), None)
        drawnGeometry = drawnArea.geometry()

        # Prepare a list to store new features
        new_features = []

        if not self.floodLayer.selectedFeatures():      # if no feature is selcted
            new_feature = QgsFeature(self.floodLayer.fields())
            new_feature.setGeometry(drawnGeometry)
            
            new_feature['Intensity'] = self.intensity

            # Add the new feature to list
            new_features.append(new_feature)

        else:

            for feature in self.floodLayer.selectedFeatures():
        
                if feature.geometry().intersects(drawnGeometry):

                    # Store the original risk level
                    org_intensity = feature['Intensity']
                    
                    # Calculate the intersection geometry
                    intersection = feature.geometry().intersection(drawnGeometry)

                    # Create a new feature for the remaining part
                    remaining_geometry = feature.geometry().difference(intersection)

                    # Update the geometry of the feature with the intersection
                    feature.setGeometry(intersection)

                    if not remaining_geometry.isEmpty():
                        new_feature = QgsFeature(self.floodLayer.fields())
                        new_feature.setGeometry(remaining_geometry)

                        new_feature['Intensity'] = org_intensity

                        # Add the new feature to list
                        new_features.append(new_feature)

                # Update the risk level attribute of the feature
                feature['Intensity'] = self.intensity

                # Update the feature in the layer
                self.floodLayer.updateFeature(feature)

        # Add new features to the layer
        if new_features:
            self.floodLayer.addFeatures(new_features)

        # Disconnect from the signal
        self.selectedArea.featureAdded.disconnect()
        self.floodLayer.removeSelection()

        # Save changes and end edit mode
        self.selectedArea.commitChanges()
        self.floodLayer.commitChanges()

        root = QgsProject.instance().layerTreeRoot()
        root.findLayer(self.selectedArea).setItemVisibilityChecked(False)
    
