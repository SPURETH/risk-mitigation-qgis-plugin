# -*- coding: utf-8 -*-

import os
import shutil
import time

from qgis.core import QgsProject, QgsEditFormConfig, QgsWkbTypes
from qgis.core import *
from qgis import processing


class GeneralFunctions:
    """This class contains functions needed multiple steps."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.absPath = QgsProject.instance().absolutePath()

    def getVectorLayer(self, filePath, layername):
        """Get a vector layer.

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

        return QgsVectorLayer(path, layerName, "delimitedtext")

    def filePresent(self, filename, extension=".shp"):
        """Check if a file exists in the specified directory.

        Args:
            filename (str): The name of the file to check for existence.

        Returns:
            bool: True if the file exists, False otherwise.
        """

        filePath = self.absPath + "/" + filename + extension
        return os.path.isfile(filePath)

    def removeShpFile(self, destFileName):
        """Remove file (not only shapefiles).

        Args:
            destFileName (str): The name of the file to remove.
        """

        files = os.listdir(self.absPath)

        for file in files:
            fileName = os.path.splitext(file)[0]
            extension = os.path.splitext(file)[1]

            if fileName == destFileName:
                filePath = self.absPath + "/" + fileName + extension

                os.remove(filePath)

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

    def resetFile(self, fileName):
        """Remove layer and shapefile from map."""

        if self.filePresent(fileName):
            self.removeLayer(fileName)
            self.removeShpFile(fileName)

    def addLayer(self, filename, style="", extension="shp"):
        """Add layer to map.

        Args:
            filename (str): Name of layer to add.
            style (str, optional): Name of style to set.
            extension(str, optional): extension of file. Default to "shp".
        """

        self.removeLayer(filename)

        layer = QgsVectorLayer(
            self.absPath + "/" + filename + f".{extension}", filename, "ogr"
        )

        if not layer.isValid():
            raise Exception("The Layer " + filename + " is not available.")

        QgsProject.instance().addMapLayer(layer)

        style_file = self.absPath + "/" + style + ".qml"
        if style != "":
            layer.loadNamedStyle(style_file)

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

            # .qix not added when creating temp file; needs to be deleted
            if extension == ".qix":
                filePath = self.absPath + "/" + fileName + extension
                os.remove(filePath)

            elif fileName == destFileName:
                newFilePathEx = tempFilePath + extension
                destinationFilePath = self.absPath + "/" + fileName + extension
                shutil.copy(newFilePathEx, destinationFilePath)

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
        fixed = processing.run(
            "native:fixgeometries",
            {"INPUT": input, "OUTPUT": "memory:"},
        )["OUTPUT"]
        lyr = processing.run(
            "qgis:clip", {"INPUT": fixed, "OVERLAY": CampExtent, "OUTPUT": "memory:"}
        )["OUTPUT"]

        return lyr

    def writeVectorLayer(self, lyr, lyrName, extension="shp"):
        """Write vector layer.

        Args:
            lyr (QgsVectorLayer): Layer to write.
            lyrName (string): Name of layer to write.
            extension(str, optional): extension of file. Default to "shp".
        """

        options = QgsVectorFileWriter.SaveVectorOptions()
        if extension == "shp":
            options.driverName = "ESRI Shapefile"
        elif extension == "gpkg":
            options.driverName = "GPKG"
        QgsVectorFileWriter.writeAsVectorFormatV3(
            lyr,
            self.absPath + "/" + lyrName + f".{extension}",
            QgsCoordinateTransformContext(),
            options,
        )

    def setLayerStyle(self, lyr, styleLyrName):
        """Set style of vetor layer.

        Args:
            lyr (QgsVectorLayer): Layer for which the style is to be set.
            lyrName (string): Name of style to be set.
        """

        style_file = self.absPath + "/" + styleLyrName + ".qml"
        feedback = QgsProcessingFeedback()
        lyrFixed = processing.run(
            "native:fixgeometries",
            {"INPUT": lyr, "OUTPUT": "memory:"},
        )["OUTPUT"]
        processing.run(
            "native:setlayerstyle",
            {"INPUT": lyrFixed, "STYLE": style_file},
            feedback=feedback,
        )

    def extractByLocation(self, inputLayer, intersectLayer: str):
        """Extract features by location.

        Args:
            inputLayer (QgsVectorLayer): Layer from which features are extracted.
            intersectLayer (QgsVectorLayer): Intersection layer.

        Returns:
            lyr (QgsVectorLayer): Extracted layer.
        """
        
        fixed = processing.run(
            "native:fixgeometries",
            {"INPUT": inputLayer,
             "OUTPUT": "memory:"},
        )["OUTPUT"]

        lyr = processing.run(
            "native:extractbylocation",
            {
                "INPUT": fixed,
                "PREDICATE": [0],
                "INTERSECT": intersectLayer,
                "OUTPUT": "memory:",
            },
        )["OUTPUT"]

        return lyr

    def isLayerEmpty(self, layerName):
        """Check if layer is empty.

        Returns:
            bool: True if the layer is empty, False otherwise.
        """

        layer = QgsVectorLayer(
            self.absPath + "/" + layerName + ".shp", layerName, "ogr"
        )

        return layer.featureCount() == 0

    def writeTempFile(self, lyr, lyrNameTemp, lyrNameDest):
        """Exchange two shapefiles / make a temporary shapefile permanent.

        Args:
            lyr (QgsVectorLayer): Layer to be made permanent.
            lyrNameTemp (str): Temporary layer name.
            lyrNameDest (str): Layer name of final location.
        """

        self.writeVectorLayer(lyr, lyrNameTemp)
        self.exchangeShpFile(lyrNameTemp, lyrNameDest)
        self.removeShpFile(lyrNameTemp)

    def fieldsExist(self, lyrName, fieldNames):
        """Exchange two shapefiles / make a temporary shapefile permanent.

        Args:
            lyrName (str): Name of layer to be checked.
            fieldNames (list of str): Names of fields to check.
        """

        lyr = QgsVectorLayer(self.absPath + "/" + lyrName + ".shp", lyrName, "ogr")

        lyrFieldNames = [field.name() for field in lyr.fields()]
        missingFields = [f for f in fieldNames if f not in lyrFieldNames]

        if not missingFields:
            return True
        else:
            return False

    
