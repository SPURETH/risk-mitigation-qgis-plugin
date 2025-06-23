# -*- coding: utf-8 -*-

import os
import shutil
import time

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsEditFormConfig,
    QgsWkbTypes,
)
from qgis.core import *
from qgis import processing
from .UNHCR_generalFunctions import GeneralFunctions
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QVariant
import pandas as pd
from shapely import wkt

class Step2:
    """This class contains all functions needed to perform step 2."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.campLayer = self._setupMap()
        self.absPath = QgsProject.instance().absolutePath()

    def _removeLayers(self):
        """Remove map layers."""

        self.generalFunctions.removeLayer("Roads")
        self.generalFunctions.removeLayer("Buildings")
        self.generalFunctions.removeLayer("RiverineFlood")
        self.generalFunctions.removeLayer("PluvialFlood")

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

    def addVectorLayer(self, filePath, layername):
        """Add a vector layer.

        Args:
            filePath (str): The path to the vector file.
            layername (str): The name to assign to the layer.

        Returns:
            QgsVectorLayer: The added vector layer.
        """

        return QgsVectorLayer(filePath, layername, "ogr")

    def addDelimitedLayer(self, filePath, layerName):
        """Add a vector layer from a csv file.

        Args:
            filePath (str): The path to the csv file.
            layername (str): The name to assign to the layer.

        Returns:
            QgsVectorLayer: The added vector layer.
        """
        
        path = (
            "file:///%s?useHeader=%s&crs=%s&delimiter=%s&decimal=%s&wktField=%s&geomType=%s"
            % (filePath, "yes", "EPSG:4326", ",", ".", "geometry", "polygon")
        )

        # Adjust layer settings
        layerOptions = 'useSpatialIndex=yes'

        return QgsVectorLayer(path, layerName, "delimitedtext", layerOptions)

    def mergeTemplate(self, lyrData, layerName, temp=""):
        """Merge vector layers with a template layer.
        Additionally, fixes geometries.

        Args:
            lyrData (str): The path to the data vector layer file.
            layerName (str): The name of the template and output layer.
            temp (str, optional): Temporary prefix for the output file name if file with layerName already exists. Defaults to "".

        """

        # used if file is already present
        outputName = temp + layerName

        templatePath = self.absPath + "/template_" + layerName + ".shp"
        lyrTemplate = QgsVectorLayer(templatePath, "template_" + layerName, "ogr")

        lyrTemplateFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrTemplate, "OUTPUT": "memory:"},
        )["OUTPUT"]
        lyrDataFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrData, "OUTPUT": "memory:"},
        )["OUTPUT"]

        processing.run(
            "qgis:mergevectorlayers",
            {
                "LAYERS": [lyrTemplateFixed, lyrDataFixed],
                "CRS": "EPSG:4326",
                #'OUTPUT': self.absPath + "/" + layerName +".shp"})["OUTPUT"]
                "OUTPUT": self.absPath + "/" + outputName + ".shp",
            },
        )["OUTPUT"]

    def filePresent(self, filename):
        """Check if a file exists in the specified directory.

        Args:
            filename (str): The name of the file to check for existence.

        Returns:
            bool: True if the file exists, False otherwise.
        """

        filePath = self.absPath + "/" + filename + ".shp"
        return os.path.isfile(filePath)

    def removeLayer(self, filename):
        """Remove layer from map.

        Args:
            filename (str): The name of the file to remove.
        """

        # if no layer with this name present, do not remove it
        if QgsProject.instance().mapLayersByName(filename):

            layer = QgsProject.instance().mapLayersByName(filename)[0]
            layer_id = layer.id()
            QgsProject.instance().removeMapLayer(layer_id)

    def addLayer(self, filename, style=""):
        """Add layer to map.

        Args:
            filename (str): Name of layer to add.
            style (str, optional): Name of style to set.
        """

        self.removeLayer(filename)

        layer = QgsVectorLayer(self.absPath + "/" + filename + ".shp", filename, "ogr")

        if style != "":
            self.setLayerStyle(layer, style)

        QgsProject.instance().addMapLayer(layer)

    def exchangeShpFile(self, tempFileName, destFileName):
        """Exchange two shapefiles / make a temporary shapefile permanent.

        Args:
            tempFileName (str): Name of layer to be made permanent.
            destFileName (str): Name of layer or be exchanged.
        """

        tempFilePath = self.absPath + "/" + tempFileName

        files = os.listdir(self.absPath)

        for file in files:
            fileName = os.path.splitext(file)[0]
            extension = os.path.splitext(file)[1]

            if fileName == destFileName:
                tempFilePathEx = tempFilePath + extension
                destinationFilePath = self.absPath + "/" + fileName + extension
                shutil.copy(tempFilePathEx, destinationFilePath)

    def prepRiverineFlood(self, filePath, RepeatYear):
        """Add Riverine flood layer and bring attribute table in correct form.

        Args:
            filePath (str): Path of raster Data.
            RepeatYear (str): Repeat year of raster data.

        Returns:
            QgsVectorLayer: Riverine Flood layer for RepeatYear.
        """

        rastRiverine = QgsRasterLayer(filePath, "rastRiverine")

        # to poligonize extent can't be too small
        extent = self.campLayer.extent()
        xmin = extent.xMinimum() - 0.004
        xmax = extent.xMaximum() + 0.004
        ymin = extent.yMinimum() - 0.004
        ymax = extent.yMaximum() + 0.004

        rastRiverine_clip = processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": rastRiverine,
                "PROJWIN": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                #'EXTENT': [xmin, xmax, ymin, ymax],
                "NODATA": "0",
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        rastRiverine_clip_100 = processing.run(
            "gdal:rastercalculator",
            {
                "INPUT_A": rastRiverine_clip,
                "BAND_A": 1,
                "FORMULA": "A * 100",
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        lyrRiverine = processing.run(
            "gdal:polygonize",
            {
                "INPUT": rastRiverine_clip_100,
                "BAND": 1,
                "FIELD": "WaterHgt",
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]
        lyrRiverineFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrRiverine, "OUTPUT": "TEMPORARY_OUTPUT"},
        )["OUTPUT"]

        lyrRiverine_attr = self.mergeTemplateReturn(lyrRiverineFixed, "FloodRiverine")

        with edit(lyrRiverine_attr):
            for feature in lyrRiverine_attr.getFeatures():
                feature["RepeatYear"] = RepeatYear
                lyrRiverine_attr.updateFeature(feature)

        return lyrRiverine_attr

    def mergeTemplateReturn(self, lyrData, layerName):
        """Merge vector layers with a template layer.
        Additionally, fixes geometries.

        Args:
            lyrData (str): The path to the data vector layer file.
            layerName (str): The name of the template and output layer.

        Returns:
            QgsVectorLayer: Merged layer.
        """

        templatePath = self.absPath + "/template_" + layerName + ".shp"
        lyrTemplate = QgsVectorLayer(templatePath, "template_" + layerName, "ogr")

        lyrTemplateFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrTemplate, "OUTPUT": "memory:"},
        )["OUTPUT"]
        lyrDataFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyrData, "OUTPUT": "memory:"},
        )["OUTPUT"]

        lyr = processing.run(
            "qgis:mergevectorlayers",
            {
                "LAYERS": [lyrTemplateFixed, lyrDataFixed],
                "CRS": "EPSG:4326",
                "OUTPUT": "memory:",
            },
        )["OUTPUT"]

        return lyr

    def clipCampArea(self, input):
        """Clip layer with settlement area.

        Args:
            input (QgsVectorLayer): Layer to be clipped.

        Returns:
            QgsVectorLayer: Clipped layer.
        """

        CampExtent = QgsVectorLayer(
            self.absPath + "/SettlementArea.shp", "SettlementArea", "ogr"
        )

        lyr = processing.run(
            "qgis:clip", {"INPUT": input, "OVERLAY": CampExtent, "OUTPUT": "memory:"}
        )["OUTPUT"]

        return lyr

    def calculateFloodIntensity(self, lyr, floodType):
        """Calculate flood intensity of features in riverine flood layer.

        Args:
            lyr (QgsVectorLayer): Riverine flood layer.
        """

        if floodType == "pluvial":

            e = QgsExpression(
                """CASE 
                                    WHEN  "WaterHgt" < 20 THEN 1
                                    WHEN  "WaterHgt" < 60 THEN 2
                                    WHEN  "WaterHgt" >= 60 THEN 3
                                    ELSE 99
                                    END"""
            )
        
        elif floodType == "riverine":

            e = QgsExpression(
                """CASE 
                                    WHEN  "WaterHgt" < 201 THEN 1
                                    WHEN  "WaterHgt" < 501 THEN 2
                                    WHEN  "WaterHgt" >= 501 THEN 3
                                    ELSE 99
                                    END"""
            )

        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for f in lyr.getFeatures():
                context.setFeature(f)
                f["Intensity"] = e.evaluate(context)
                lyr.updateFeature(f)

    def writeVectorLayer(self, lyr, lyrName):
        """Write vector layer.

        Args:
            lyr (QgsVectorLayer): Layer to write.
            lyrName (string): Name of layer to write.
        """

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        QgsVectorFileWriter.writeAsVectorFormatV3(
            lyr, self.absPath + lyrName, QgsCoordinateTransformContext(), options
        )

    def setLayerStyle(self, lyr, styleLyrName):
        """Set style of vetor layer.

        Args:
            lyr (QgsVectorLayer): Layer for which the style is to be set.
            lyrName (string): Name of style to be set.
        """

        style_file = self.absPath + styleLyrName
        feedback = QgsProcessingFeedback()
        processing.run(
            "native:setlayerstyle",
            {"INPUT": lyr, "STYLE": style_file},
            feedback=feedback,
        )

    def uploadRoadData(self, filePath):
        """Upload road data.

        Args:
            filepath (string): Path of shapefile containing road data.
        """

        lyr = self.generalFunctions.getVectorLayer(filePath, "Roads")
        lyrClip = self.generalFunctions.clipCampArea(lyr)
        self.mergeTemplate(lyrClip, "Roads")

    def addFields(self, lyr, fields_needed):
        """Add fields to the given layer.
        
        Args:
            lyr (QgsVectorLayer): Layer to which fields are added.

            fields_needed (dict): Names and types of fields to add.
        """

        fields_existing = [field.name() for field in lyr.fields()]
        missing_fields = [field for field in list(fields_needed.keys()) if field not in fields_existing]

        qgsFields = []
        for field in missing_fields:
            qgsFields.append(QgsField(field, fields_needed.get(field)))

        lyr.dataProvider().addAttributes(qgsFields)
        lyr.updateFields()

    def checkForNullValue(self, lyr, fieldName, value):
        # Start an edit session
        #lyr.startEditing()

        # Iterate over features and update empty values
        # for feature in lyr.getFeatures():
        #     current_value = feature[fieldName]
        #     if QgsExpression.isNull(current_value):  # Check for NULL
        #         feature[fieldName] = value  # Set the value
        #         lyr.updateFeature(feature)

        # Create an expression to handle NULL values
        e = QgsExpression(f"CASE WHEN \"{fieldName}\" IS NULL THEN {value} ELSE \"{fieldName}\" END")

        # e = QgsExpression(
        #         """CASE 
        #                             WHEN  "Intensity" is NULL THEN 99
        #                             ELSE "Intensity"
        #                             END"""
        #     )

        # Create the expression context
        # context = QgsExpressionContext()
        # context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        # # Loop through features and evaluate the expression
        # for feature in lyr.getFeatures():
        #     context.setFeature(feature)  # Set the current feature for evaluation
        #     new_value = expression.evaluate(context)  # Evaluate the expression with the context
        #     feature.setAttribute(fieldName, new_value)  # Set the updated value
        #     lyr.updateFeature(feature)  # Update the feature


        # Commit changes
        #lyr.commitChanges()


        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(lyr))

        with edit(lyr):
            for f in lyr.getFeatures():
                context.setFeature(f)
                f[fieldName] = e.evaluate(context)
                lyr.updateFeature(f)