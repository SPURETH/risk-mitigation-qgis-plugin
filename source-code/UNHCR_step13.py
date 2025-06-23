# -*- coding: utf-8 -*-

import pathlib
import sys
import os
from .installer import installer_func

installer_func()
import pandas as pd
import processing
from .UNHCR_generalFunctions import GeneralFunctions
from qgis.core import *

from qgis.core import QgsProject, QgsEditFormConfig


class Step13:
    """This class contains all functions needed to perform step 13."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.absPath = QgsProject.instance().absolutePath()
        self.generalFunctions = GeneralFunctions(self.iface)
        self._removeLayers()

    def _removeLayers(self):
        """Remove 'Measures' layers that are not used anymore."""

        self.generalFunctions.removeLayer("Measures_Pluvial_Building")
        self.generalFunctions.removeLayer("Measures_Riverine_Building")
        self.generalFunctions.removeLayer("Measures_Pluvial_Road")
        self.generalFunctions.removeLayer("Measures_Riverine_Road")
        self.generalFunctions.removeLayer("Measures_Pluvial_TechnicalInfrastructure")
        self.generalFunctions.removeLayer("Measures_Riverine_TechnicalInfrastructure")
        self.generalFunctions.removeLayer("Measures_Pluvial_LandCover")
        self.generalFunctions.removeLayer("Measures_Riverine_LandCover")

    def getMeasuresDf(self, layer):
        """Create a pandas DataFrame from the features of a QgsVectorLayer.

        Args:
            layer (QgsVectorLayer): The vector layer from which to extract features.

        Returns:
            pandas.DataFrame: A DataFrame containing the attributes of the features in the layer.
        """

        # List all columns you want to include in the dataframe
        cols = [f.name() for f in layer.fields()]

        # A generator to yield one row at a time
        datagen = ([f[col] for col in cols] for f in layer.getFeatures())

        return pd.DataFrame(datagen, columns=cols)

    def getCheckedMeasures(self, dfMeasures, dfChecks, category):
        """Filter measures based on chosen categories.

        Args:
            dfMeasures (pandas.DataFrame): DataFrame containing measures data.
            dfChecks (pandas.DataFrame): DataFrame containing checks data.
            category (str): The category to filter measures.

        Returns:
            numpy.ndarray: An array containing feature IDs corresponding to the filtered measures.
        """

        checkedNames = [string for string in dfChecks.columns if category in string]

        dfMeasures = dfMeasures[checkedNames]
        dfChecks = dfChecks[checkedNames]

        def is_similar(row):
            return any(
                row[row == 1] == dfChecks.iloc[0][row == 1]
            )  # get rows where Checks and Measure are similar AND 1

        # Apply the similarity check function to each row of the larger DataFrame
        similar_rows = dfMeasures.apply(is_similar, axis=1)

        # Filter the similar rows from the larger DataFrame
        similar_rows_df = dfMeasures[similar_rows].reset_index()

        # returns array with feature id corresponding to attribute table
        return similar_rows_df["index"].to_numpy()

    def getMeasuresApp(self, dfMeasures, app: str):
        """Get measures for a specific application (e.g. pluvial, riverine, buildings etc.)
        
        Args:
            dfMeasures (pandas.DataFrame): DataFrame containing measures data.
            app (str): The application to filter measures.
        """

        measures = dfMeasures[dfMeasures[app] == 1].reset_index()
        return measures["index"].to_numpy()

    def selectFeatures(self, layer, featureIds):
        """Select features in a layer based on their IDs.

        Args:
            layer (QgsVectorLayer): The vector layer containing the features.
            featureIds (list): A list of feature IDs to select.
        """

        layer.removeSelection()
        featureIds = featureIds + 2  # feature ID in QGIS attribute table beginns at 2
        layer.select(featureIds.tolist())

    def createLayer(self, layer, measures, outputName):
        """Create a new vector layer containing selected features from an input layer.

        Args:
            layer (QgsVectorLayer): The input vector layer containing the features.
            measures (list): A list of feature IDs to select.
            outputName (str): The name to be given to the output vector layer.
        """

        self.selectFeatures(layer, measures)

        path = self.absPath + "/" + outputName + ".geojson"

        if os.path.isfile(path):
            os.remove(path)
        processing.run("native:saveselectedfeatures", {"INPUT": layer, "OUTPUT": path})

        layer = QgsVectorLayer(path, outputName, "ogr")
        QgsProject.instance().addMapLayer(layer)
