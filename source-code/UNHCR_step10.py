# -*- coding: utf-8 -*-

import os
from .UNHCR_generalFunctions import GeneralFunctions

from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject
from qgis.core import *
from qgis import processing


class Step10:
    """This class contains all functions needed to perform step 10."""

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

    def spatialJoin(self, lyrNameClip, lyrNameFlood, lyrNameOutput):
        """Spatially join asset layer and flood layer.
        
        Args:
            lyrNameClip (str): Name of asset layer.
            lyrNameFlood (str): Name of flood layer.
            lyrNameOutput (str): Name of output layer.
        """

        lyrPahtClip = self.absPath + "/" + lyrNameClip + ".shp"
        lyrPathFlood = self.absPath + "/" + lyrNameFlood + ".shp"
        lyrPathOutput = self.absPath + "/" + lyrNameOutput + ".shp"

        lyrClip = self.generalFunctions.getVectorLayer(lyrPahtClip, lyrNameClip)
        lyrFlood = self.generalFunctions.getVectorLayer(lyrPathFlood, lyrNameFlood)

        lyrClipFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrClip, "OUTPUT": "memory:"},
        )["OUTPUT"]
        lyrFloodFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrFlood, "OUTPUT": "memory:"},
        )["OUTPUT"]
        lyrIntersection = processing.run(
            "qgis:intersection",
            {"INPUT": lyrClipFixed, "OVERLAY": lyrFloodFixed, "OUTPUT": "memory:"},
        )["OUTPUT"]

        lyrDifference = processing.run(
            "qgis:difference",
            {"INPUT": lyrClipFixed, "OVERLAY": lyrFloodFixed, "OUTPUT": "memory:"},
        )["OUTPUT"]

        processing.run(
            "qgis:mergevectorlayers",
            {
                "LAYERS": [lyrIntersection, lyrDifference],
                "CRS": "EPSG:4326",
                "OUTPUT": lyrPathOutput,
            },
        )["OUTPUT"]

    def addFields(self, lyr):
        """Add vulnerability and risk fields to the given layer.
        
        Args:
            lyr (QgsVectorLayer): Layer to which fields are added.
        """

        lyr.dataProvider().addAttributes(
            [
                QgsField("PhysicalVu", QVariant.Int),
                QgsField("SocEcoVu", QVariant.Int),
                QgsField("TempSumVul", QVariant.Int),
                QgsField("SumVul", QVariant.Int),
            ]
        )
        lyr.updateFields()

    def evaluateContext(self, lyr, field, expression: QgsExpression):
        """ Evaluates the provided expression for each feature in the given vector layer (`lyr`)
        and updates the specified field (`field`) with the result of the expression evaluation.

        Args:
            lyr (QgsVectorLayer): The vector layer to which the expression will be applied.
            field (str): The name of the field to be updated with the expression result.
            expression (QgsExpression): The expression to be evaluated for each feature.
        """

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for feature in lyr.getFeatures():
                context.setFeature(feature)
                feature[field] = expression.evaluate(context)
                lyr.updateFeature(feature)

    def evaluateContextInt(self, lyr, field, value: int):
        """Update the specified integer field for each feature in the layer with the given value.

        Args:
            lyr (QgsVectorLayer): The vector layer containing the features to be updated.
            field (str): The name of the integer field to be updated.
            value (int): The integer value to set for the specified field in each feature.
        """

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for feature in lyr.getFeatures():
                context.setFeature(feature)
                feature[field] = value
                lyr.updateFeature(feature)

    def setValuesBuildingsRiv(self, lyr):
        """Set values for vulnerability and risk fields of buildings prone to riverine flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_phydVul = QgsExpression(
            """CASE  
	                                    WHEN "type"  = 'emergency' AND  "Hazard" = '3' THEN 3
	                                    WHEN "type"  = 'emergency' AND  "Hazard" = '2' THEN 3
	                                    WHEN "type"  = 'emergency' AND  "Hazard" = '1' THEN 2

	                                    WHEN "type"  = 'transitional' AND  "Hazard" = '3' THEN 3	
	                                    WHEN "type"  = 'transitional' AND  "Hazard" = '2' THEN 2	
	                                    WHEN "type"  = 'transitional' AND  "Hazard" = '1' THEN 1	
	
	                                    WHEN "type"  = 'durable' AND  "Hazard" = '3' THEN 3
	                                    WHEN "type"  = 'durable' AND  "Hazard" = '2' THEN 1
	                                    WHEN "type"  = 'durable' AND  "Hazard" = '1' THEN 1

	                                    WHEN "Hazard" = '3' THEN 3
	                                    WHEN "Hazard" = '2' THEN 2
	                                    WHEN "Hazard" = '1' THEN 1
	
	                                    ELSE 0
                                   END"""
        )

        e_socioEcoVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'ResidentialShelters' THEN 2
	                                    WHEN "assets" = 'SocialInfrastructure' THEN 1
	                                    WHEN "assets" = 'OpenSpaces' THEN 1
	                                    WHEN "assets" = 'AdministrativeBuildings' THEN 1	
	                                    WHEN "assets" = 'Logistics' THEN 1	
	                                    	
	                                    ELSE 0
                                   END"""
        )

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContext(lyr, "PhysicalVu", e_phydVul)
        self.evaluateContext(lyr, "SocEcoVu", e_socioEcoVul)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)

    def setValuesBuildingsPluv(self, lyr):
        """Set values for vulnerability and risk fields of buildings prone to pluvial flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_phydVul = QgsExpression(
            """CASE  
	                                    WHEN "type"  = 'transitional' AND "Hazard" = '3' THEN 3
	                                    WHEN "type"  = 'transitional' AND "Hazard" = '2' THEN 3
	                                    WHEN "type"  = 'transitional' AND "Hazard" = '1' THEN 2
                                                                                
	                                    WHEN "type"  = 'emergency' AND "Hazard" = '3' THEN 3
	                                    WHEN "type"  = 'emergency' AND "Hazard" = '2' THEN 2
	                                    WHEN "type"  = 'emergency' AND "Hazard" = '1' THEN 1
                                                                                
	                                    WHEN "type"  = 'durable' AND "Hazard" = '3' THEN 3
	                                    WHEN "type"  = 'durable' AND "Hazard" = '2' THEN 1
	                                    WHEN "type"  = 'durable' AND "Hazard" = '1' THEN 1
                                        
                                        WHEN "Hazard" = 3 THEN 3
                                        WHEN "Hazard" = 2 THEN 2
                                        WHEN "Hazard" = 1 THEN 1
                                        	                                    	
	                                    ELSE 0
                                   END"""
        )

        e_socioEcoVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'ResidentialShelters' THEN 2
	                                    WHEN "assets" = 'SocialInfrastructure' THEN 1
	                                    WHEN "assets" = 'OpenSpaces' THEN 1
	                                    WHEN "assets" = 'AdministrativeBuildings' THEN 1	
	                                    WHEN "assets" = 'Logistics' THEN 1	
	                                    	
	                                    ELSE 0
                                   END"""
        )

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContext(lyr, "PhysicalVu", e_phydVul)
        self.evaluateContext(lyr, "SocEcoVu", e_socioEcoVul)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)

    def setValuesRoadsPluv(self, lyr):
        """Set values for vulnerability and risk fields of roads prone to pluvial flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContextInt(lyr, "PhysicalVu", 2)
        self.evaluateContextInt(lyr, "SocEcoVu", 3)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)

    def setValuesRoadsRiv(self, lyr):
        """Set values for vulnerability and risk fields of roads prone to riverine flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContextInt(lyr, "PhysicalVu", 2)
        self.evaluateContextInt(lyr, "SocEcoVu", 3)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)

    def setValuesInfrastructurePluv(self, lyr):
        """Set values for vulnerability and risk fields of infrastructure prone to pluvial flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_phydVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'PowerStation' THEN 3
	                                    WHEN "assets" = 'PowerGrid' THEN 1
	                                    WHEN "assets" = 'SanitationNetworks' THEN 1
	                                    WHEN "assets" = 'WaterTanks' THEN 1
	                                    WHEN "assets" = 'DrainageSystem' THEN 2
	                                    WHEN "assets" = 'CommunicationInfrastructure' THEN 1
	                                    
	                                    ELSE 0
                                   END"""
        )

        e_socioEcoVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'PowerStation' THEN 3
	                                    WHEN "assets" = 'PowerGrid' THEN 3
	                                    WHEN "assets" = 'SanitationNetworks' THEN 3
	                                    WHEN "assets" = 'WaterTanks' THEN 3
	                                    WHEN "assets" = 'DrainageSystem' THEN 2
	                                    WHEN "assets" = 'CommunicationInfrastructure' THEN 3
	                                    
	                                    ELSE 0
                                   END"""
        )

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = '1' AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = '2' AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = '3' AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContext(lyr, "PhysicalVu", e_phydVul)
        self.evaluateContext(lyr, "SocEcoVu", e_socioEcoVul)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)

    def setValuesInfrastructureRiv(self, lyr):
        """Set values for vulnerability and risk fields of infrastructure prone to riverine flood.

        Args:
            lyr (QgsVectorLayer): The vector layer to which values will be assigned.
        """

        e_phydVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'PowerStation' THEN 3
	                                    WHEN "assets" = 'PowerGrid' THEN 1
	                                    WHEN "assets" = 'SanitationNetworks' THEN 1
	                                    WHEN "assets" = 'WaterTanks' THEN 1
	                                    WHEN "assets" = 'DrainageSystem' THEN 2
	                                    WHEN "assets" = 'CommunicationInfrastructure' THEN 1
	                                    
	                                    ELSE 0
                                   END"""
        )

        e_socioEcoVul = QgsExpression(
            """CASE  
	                                    WHEN "assets" = 'PowerStation' THEN 3
	                                    WHEN "assets" = 'PowerGrid' THEN 3
	                                    WHEN "assets" = 'SanitationNetworks' THEN 3
	                                    WHEN "assets" = 'WaterTanks' THEN 3
	                                    WHEN "assets" = 'DrainageSystem' THEN 2
	                                    WHEN "assets" = 'CommunicationInfrastructure' THEN 3
	                                    
	                                    ELSE 0
                                   END"""
        )

        e_tempSumVul = QgsExpression(
            """CASE  
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 0 THEN 0
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 1 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 2 THEN 1
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 3 THEN 2
	                                    WHEN "PhysicalVu" + "SocEcoVu" = 4 THEN 2

	                                    ELSE 3
                                   END"""
        )

        e_sumVul = QgsExpression(
            """CASE  
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 1 THEN 1
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 2 THEN 2
	                                    WHEN "Hazard" = 1 AND "TempSumVul" = 3 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 1 THEN 2
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 2 THEN 3
	                                    WHEN "Hazard" = 2 AND "TempSumVul" = 3 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 1 THEN 3
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 2 THEN 4
	                                    WHEN "Hazard" = 3 AND "TempSumVul" = 3 THEN 5

	                                    ELSE 0
                                   END"""
        )

        self.evaluateContext(lyr, "PhysicalVu", e_phydVul)
        self.evaluateContext(lyr, "SocEcoVu", e_socioEcoVul)
        self.evaluateContext(lyr, "TempSumVul", e_tempSumVul)
        self.evaluateContext(lyr, "SumVul", e_sumVul)
