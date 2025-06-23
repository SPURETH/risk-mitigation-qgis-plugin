# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject, QgsEditFormConfig
from qgis import processing
from qgis.core import *
from .UNHCR_generalFunctions import GeneralFunctions


class Step5:
    """This class contains all functions needed to perform step 5."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.campLayer = self._setupMap()
        self.absPath = QgsProject.instance().absolutePath()

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

    def calculateHazard(self, lyr, floodType):
        """Calculate hazard of flood features.
        
        Args:
            lyr (QgsVectorLayer): Flood risk layer.
        """

        if floodType == "riverine":

            e = QgsExpression(
                """CASE  
                                    WHEN "RepeatYear" > 99 AND  "Intensity" = 3 THEN 2
                                    WHEN "RepeatYear" > 99 AND  "Intensity" = 2 THEN 2
                                    WHEN "RepeatYear" > 99 AND  "Intensity" = 1 THEN 1
                                    WHEN "RepeatYear" > 19 AND  "Intensity" = 3 THEN 3
                                    WHEN "RepeatYear" > 19 AND  "Intensity" = 2 THEN 2
                                    WHEN "RepeatYear" > 19 AND  "Intensity" = 1 THEN 1
                                    WHEN "RepeatYear" > 4 AND  "Intensity" = 3 THEN 3
                                    WHEN "RepeatYear" > 4 AND  "Intensity" = 2 THEN 2
                                    WHEN "RepeatYear" > 4 AND  "Intensity" = 1 THEN 2
                                    WHEN "Intensity" = 3 THEN 3
                                    WHEN "Intensity" = 2 THEN 3
                                    WHEN "Intensity" = 1 THEN 2
                                    WHEN "Intensity" = 99 Then 99
                                    ELSE 0	
                                END"""
            )

        elif floodType == "pluvial":
            e = QgsExpression(
                """CASE  
                                    WHEN "Intensity" = 3 THEN 3
                                    WHEN "Intensity" = 2 AND "YrlyFlood" = 1 THEN 3
                                    WHEN "Intensity" = 2 AND "YrlyFlood" = 0 THEN 2
                                    WHEN "Intensity" = 1 AND "YrlyFlood" = 1 THEN 2
                                    WHEN "Intensity" = 1 AND "YrlyFlood" = 0 THEN 1
                                    WHEN "Intensity" = 99 Then 99
                                    ELSE 0
                                END"""
            )

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for feature in lyr.getFeatures():
                context.setFeature(feature)
                feature["Hazard"] = e.evaluate(context)
                lyr.updateFeature(feature)

    def prepRoadData(slef, lyr):
        """Bring road data into correct form.
        
        Args:
            lyr (QgsVectorLayer): Road layer.
        """

        e = QgsExpression(
            """CASE 
                        WHEN  "bridge" = 'T' THEN 'bridge'
                        ELSE 'road'
                        END"""
        )

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for feature in lyr.getFeatures():
                context.setFeature(feature)
                feature["assets"] = "InternalRoadsAndWalkways"
                feature["type"] = e.evaluate(context)
                lyr.updateFeature(feature)

    def prepBuildingsData(self, lyr):
        """Bring buildings data into correct form.
        
        Args:
            lyr (QgsVectorLayer): Buildings layer.
        """

        with edit(lyr):
            for feature in lyr.getFeatures():
                feature["assets"] = "ResidentialShelters"
                feature["type"] = "transitional"
                lyr.updateFeature(feature)