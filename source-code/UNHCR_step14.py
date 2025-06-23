# -*- coding: utf-8 -*-

import pathlib
import sys
import os
from .installer import installer_func

installer_func()
import pandas as pd

from qgis.core import QgsProject, QgsEditFormConfig, QgsTextFormat, QgsLayoutItemLabel
from qgis.core import *
from PyQt5.QtGui import QFont
from qgis import processing
from PyQt5.QtCore import Qt, QDateTime, QEventLoop
from .UNHCR_generalFunctions import GeneralFunctions
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from .UNHCR_dialog_layoutManager import LayoutManager

class Step14:
    """This class contains all functions needed to perform step 14."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.absPath = QgsProject.instance().absolutePath()
        self.layoutManager = QgsProject.instance().layoutManager()
        self.generalFunctions = GeneralFunctions(self.iface)
        self._removeLayouts()

    def _removeLayouts(self):
        """Remove previously used layouts."""

        for layout in self.layoutManager.layouts():
            self.layoutManager.removeLayout(layout)

    def setupMap(self, layerName):
        """Setup map layers and visibility.
        
        Args:
            layerName (list of str): List of layer names to be made visible on the map.
        """

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()
        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        if "Roads" in layerName:
            self.generalFunctions.addLayer(layerName, "LayerStyle_Step10_Line")
        else:
            self.generalFunctions.addLayer(layerName, "LayerStyle_Step10_Polygon")

        lyrshow = QgsProject.instance().mapLayersByName(layerName)[0]
        root.findLayer(lyrshow).setItemVisibilityChecked(True)

    def setupMapEmpty(self):
        """Setup an empty map with no layers visible except for Basemap."""

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()
        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

    def exportLayoutAsPDF(self, layoutName, titleText, layerName, exportName, checksText):
        """Setup print layout and export it as PDF file.
        
        Args:
            layoutName (str): Name to be given to the layout.
            titleText (str): Title to be added to the PDF.
            layerName (str): Name of the layer containing the suitable measures.
            exportName (str): Name of the PDF file to be exported.
            checksText (list of str): List of names of checked characterisitcs.
        """

        layout = QgsPrintLayout(QgsProject.instance())

        # initializes default settings for blank print layout canvas
        layout.initializeDefaults()

        layout.setName(layoutName)
        self.layoutManager.addLayout(layout)

        ### manually adjust layout

        # # Load the .qpt file
        # qpt_file_path = self.absPath + "/Test_LayoutTemplate.qpt"
        # with open(qpt_file_path, 'r') as f:
        #     template_content = f.read()

        # # Use QDomDocument to parse the .qpt file
        # doc = QDomDocument()
        # doc.setContent(template_content)

        # # Load the template into the layout
        # layout.loadFromTemplate(doc, QgsReadWriteContext())

        # # Optionally, set the layout as active in QGIS interface
        # #iface.openLayoutDesigner(layout)

        # # Open the Layout Designer
        # layout_designer = iface.openLayoutDesigner(layout)

        # # Run a blocking event loop until the layout designer is closed
        # layout_designer.exec_()

        ###


        # second page
        page = QgsLayoutItemPage(layout)
        page.setPageSize("A4", QgsLayoutItemPage.Landscape)
        layout.pageCollection().addPage(page)

        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)

        # Set Map Extent
        campArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        campExtent = campArea.extent()

        bufferedExtent = QgsRectangle(
            campExtent.xMinimum() - 0.002,
            campExtent.yMinimum() - 0.002,
            campExtent.xMaximum() + 0.002,
            campExtent.yMaximum() + 0.002,
        )

        map.setExtent(bufferedExtent)

        layout.addLayoutItem(map)

        # Move & Resize map on print layout canvas
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(230, 178, QgsUnitTypes.LayoutMillimeters))

        # Title
        title = QgsLayoutItemLabel(layout)

        title.setText(titleText)
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(20)
        title.setTextFormat(textFormatTitle)

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))

        # Legend
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        layout.addLayoutItem(legend)

        legend.setLinkedMap(map)  # pass a QgsLayoutItemMap object
        legend.setLegendFilterByMapEnabled(True)
        legend.refresh()
        legend.attemptMove(QgsLayoutPoint(237, 25, QgsUnitTypes.LayoutMillimeters))

        # Date
        currentDate = QDateTime.currentDateTime().toString("dd-MM-yyyy")
        date = QgsLayoutItemLabel(layout)
        date.setText(currentDate)
        textFormatDate = date.textFormat()
        fontDate = QFont("Helvetica")
        textFormatDate = QgsTextFormat()
        textFormatDate.setFont(fontDate)
        textFormatDate.setSize(8)
        date.setTextFormat(textFormatDate)
        date.attemptMove(QgsLayoutPoint(10, 15, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(date)

        # Scale
        scale = QgsLayoutItemLabel(layout)
        scale.setText(f"Scale 1:{int(layout.referenceMap().scale())}")

        textFormatScale = scale.textFormat()
        fontScale = QFont("Helvetica")
        textFormatScale = QgsTextFormat()
        textFormatScale.setFont(fontScale)
        textFormatScale.setSize(10)
        scale.setTextFormat(textFormatScale)
        scale.attemptMove(QgsLayoutPoint(10, 200, QgsUnitTypes.LayoutMillimeters))
        layout.addItem(scale)

        # Title categories
        title = QgsLayoutItemLabel(layout)

        title.setText("Selected Characteristics")
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        fontTitle.setBold(True)
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(12)
        title.setTextFormat(textFormatTitle)

        layout.refresh()

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 15, QgsUnitTypes.LayoutMillimeters), page=1)

        # Categories
        categories = {
            'Type of Intervention': ['Engineered', 'Nature-Based', 'Hybrid', 'Non-Structural'],
            'Scale of Intervention': ['Shelter-Plot-Block', 'Settlement', 'Supra-settlement'],
            'Targeted Hazard': ['Pluvial Flood', 'Coastal/Riverine Flood'],
            'Targeted Vulnerable Assets': ['Buildings', 'Transport', 'Technical Infrastructure', 'Land Cover'],
            'Strategy Type': ['Relocate', 'Reduce Hazard Magnitude', 'Reduce Asset Vulnerability', 'Reduce Casualities'],
            'Implementation Time': ['Short (1 day - 1 month)', 'Medium (1 month - 1 year)', 'Long (> 1 year)'],
            'Effect Duration': ['Short-term (<  1 year)', 'Medium-term (1 year to 10 years)', 'Long-term (> 10 years)'],
            'Investment Costs': ['Low', 'Medium', 'High'],
            'Maintenance Costs (yearly)': ['Low (< 10% investment costs)', 'Medium (10-50%)', 'High (> 50%)']
        }

        headers = '\n\n'.join(categories.keys())

        values = '\n\n'.join(', '.join(value for value in values if value in checksText) for values in categories.values())

        # Add a layout item (text)
        text_item = QgsLayoutItemLabel(layout)
        text_item.setText(headers)

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(10)
        text_item.setTextFormat(textFormatTitle)

        text_item.attemptMove(QgsLayoutPoint(10, 23, QgsUnitTypes.LayoutMillimeters), page=1)

        # Add the text item to the layout
        layout.addLayoutItem(text_item)

        values_item = QgsLayoutItemLabel(layout)
        values_item.setText(values)

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(10)
        values_item.setTextFormat(textFormatTitle)

        values_item.attemptMove(QgsLayoutPoint(70, 23, QgsUnitTypes.LayoutMillimeters), page=1)

        # Add the text item to the layout
        layout.addLayoutItem(values_item)

        # Title table
        title = QgsLayoutItemLabel(layout)

        title.setText("Suitable Measures")
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        fontTitle.setBold(True)
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(12)
        title.setTextFormat(textFormatTitle)

        layout.refresh()

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 95, QgsUnitTypes.LayoutMillimeters), page=1)

        # Table
        lyrtable = QgsProject.instance().mapLayersByName(layerName)[0]

        table = QgsLayoutItemAttributeTable(layout)
        table.setVectorLayer(lyrtable)

        # add columns
        cols = table.columns()
        new_cols = cols

        new_cols[0].setWidth(30)
        new_cols[0].setHAlignment(Qt.AlignLeft)
        new_cols[1].setWidth(120)  # 130
        new_cols[1].setHAlignment(Qt.AlignLeft)

        # Set 'table' columns from the list of cloned and modified column objects
        table.setColumns([new_cols[0], new_cols[1]])
        table.refresh()
 
        # Base class for frame items, which form a layout multiframe item.
        frame = QgsLayoutFrame(layout, table)
        frame.attemptResize(QgsLayoutSize(210, 210), True)
        frame.attemptMove(
            QgsLayoutPoint(10, 102, QgsUnitTypes.LayoutMillimeters), page=1
        )
        table.addFrame(frame)

        # this accesses a specific layout, by name (which is a string)
        layout = self.layoutManager.layoutByName(layoutName)

        ### manually adjust layout

        #self.iface.openLayoutDesigner(layout)

        #dlgLayoutManager = LayoutManager(layout, self.iface)

        ###

        # this creates a QgsLayoutExporter object
        exporter = QgsLayoutExporter(layout)

        # this exports a pdf of the layout object
        exportPath = self.absPath + "/Measures" + "/" + exportName + ".pdf"
        exporter.exportToPdf(exportPath, QgsLayoutExporter.PdfExportSettings())

    def createLayout(self, titleText, layerName, checksText):
        """Setup print layout and export it as PDF file.
        
        Args:
            layoutName (str): Name to be given to the layout.
            titleText (str): Title to be added to the PDF.
            layerName (str): Name of the layer containing the suitable measures.
            exportName (str): Name of the PDF file to be exported.
            checksText (list of str): List of names of checked characterisitcs.
        """

        layout = QgsPrintLayout(QgsProject.instance())

        # initializes default settings for blank print layout canvas
        layout.initializeDefaults()

        #layout.setName(layoutName)
        self.layoutManager.addLayout(layout)

        # second page
        page = QgsLayoutItemPage(layout)
        page.setPageSize("A4", QgsLayoutItemPage.Landscape)
        layout.pageCollection().addPage(page)

        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)

        # Set Map Extent
        campArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        campExtent = campArea.extent()

        bufferedExtent = QgsRectangle(
            campExtent.xMinimum() - 0.002,
            campExtent.yMinimum() - 0.002,
            campExtent.xMaximum() + 0.002,
            campExtent.yMaximum() + 0.002,
        )

        map.setExtent(bufferedExtent)

        layout.addLayoutItem(map)

        # Move & Resize map on print layout canvas
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(230, 178, QgsUnitTypes.LayoutMillimeters))

        # Title
        title = QgsLayoutItemLabel(layout)

        title.setText(titleText)
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(20)
        title.setTextFormat(textFormatTitle)

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 6, QgsUnitTypes.LayoutMillimeters))

        # Legend
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Legend")
        layout.addLayoutItem(legend)

        legend.setLinkedMap(map)  # pass a QgsLayoutItemMap object
        legend.setLegendFilterByMapEnabled(True)
        legend.refresh()
        legend.attemptMove(QgsLayoutPoint(237, 25, QgsUnitTypes.LayoutMillimeters))

        # Date
        currentDate = QDateTime.currentDateTime().toString("dd-MM-yyyy")
        date = QgsLayoutItemLabel(layout)
        date.setText(currentDate)
        textFormatDate = date.textFormat()
        fontDate = QFont("Helvetica")
        textFormatDate = QgsTextFormat()
        textFormatDate.setFont(fontDate)
        textFormatDate.setSize(8)
        date.setTextFormat(textFormatDate)
        date.attemptMove(QgsLayoutPoint(10, 15, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(date)

        # Scale
        scale = QgsLayoutItemLabel(layout)
        scale.setText(f"Scale 1:{int(layout.referenceMap().scale())}")

        textFormatScale = scale.textFormat()
        fontScale = QFont("Helvetica")
        textFormatScale = QgsTextFormat()
        textFormatScale.setFont(fontScale)
        textFormatScale.setSize(10)
        scale.setTextFormat(textFormatScale)
        scale.attemptMove(QgsLayoutPoint(10, 200, QgsUnitTypes.LayoutMillimeters))
        layout.addItem(scale)

        # Title categories
        title = QgsLayoutItemLabel(layout)

        title.setText("Selected Characteristics")
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        fontTitle.setBold(True)
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(12)
        title.setTextFormat(textFormatTitle)

        layout.refresh()

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 15, QgsUnitTypes.LayoutMillimeters), page=1)

        # Categories
        categories = {
            'Type of Intervention': ['Engineered', 'Nature-Based', 'Hybrid', 'Non-Structural'],
            'Scale of Intervention': ['Shelter-Plot-Block', 'Settlement', 'Supra-settlement'],
            'Targeted Hazard': ['Pluvial Flood', 'Coastal/Riverine Flood'],
            'Targeted Vulnerable Assets': ['Buildings', 'Transport', 'Technical Infrastructure', 'Land Cover'],
            'Strategy Type': ['Relocate', 'Reduce Hazard Magnitude', 'Reduce Asset Vulnerability', 'Reduce Casualities'],
            'Implementation Time': ['Short (1 day - 1 month)', 'Medium (1 month - 1 year)', 'Long (> 1 year)'],
            'Effect Duration': ['Short-term (<  1 year)', 'Medium-term (1 year to 10 years)', 'Long-term (> 10 years)'],
            'Investment Costs': ['Low', 'Medium', 'High'],
            'Maintenance Costs (yearly)': ['Low (< 10% investment costs)', 'Medium (10-50%)', 'High (> 50%)']
        }

        headers = '\n\n'.join(categories.keys())

        values = '\n\n'.join(', '.join(value for value in values if value in checksText) for values in categories.values())

        # Add a layout item (text)
        text_item = QgsLayoutItemLabel(layout)
        text_item.setText(headers)

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(10)
        text_item.setTextFormat(textFormatTitle)

        text_item.attemptMove(QgsLayoutPoint(10, 23, QgsUnitTypes.LayoutMillimeters), page=1)

        # Add the text item to the layout
        layout.addLayoutItem(text_item)

        values_item = QgsLayoutItemLabel(layout)
        values_item.setText(values)

        fontTitle = QFont("Helvetica")
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(10)
        values_item.setTextFormat(textFormatTitle)

        values_item.attemptMove(QgsLayoutPoint(70, 23, QgsUnitTypes.LayoutMillimeters), page=1)

        # Add the text item to the layout
        layout.addLayoutItem(values_item)

        # Title table
        title = QgsLayoutItemLabel(layout)

        title.setText("Suitable Measures")
        textFormatTitle = title.textFormat()

        fontTitle = QFont("Helvetica")
        fontTitle.setBold(True)
        textFormatTitle = QgsTextFormat()
        textFormatTitle.setFont(fontTitle)
        textFormatTitle.setSize(12)
        title.setTextFormat(textFormatTitle)

        layout.refresh()

        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 95, QgsUnitTypes.LayoutMillimeters), page=1)

        # Table
        lyrtable = QgsProject.instance().mapLayersByName(layerName)[0]

        table = QgsLayoutItemAttributeTable(layout)
        table.setVectorLayer(lyrtable)

        # add columns
        cols = table.columns()
        new_cols = cols

        new_cols[0].setWidth(30)
        new_cols[0].setHAlignment(Qt.AlignLeft)
        new_cols[1].setWidth(120)  # 130
        new_cols[1].setHAlignment(Qt.AlignLeft)

        # Set 'table' columns from the list of cloned and modified column objects
        table.setColumns([new_cols[0], new_cols[1]])
        table.refresh()
 
        # Base class for frame items, which form a layout multiframe item.
        frame = QgsLayoutFrame(layout, table)
        frame.attemptResize(QgsLayoutSize(210, 210), True)
        frame.attemptMove(
            QgsLayoutPoint(10, 102, QgsUnitTypes.LayoutMillimeters), page=1
        )
        table.addFrame(frame)

        # this accesses a specific layout, by name (which is a string)
        #layout = self.layoutManager.layoutByName(layoutName)

        return layout
    
    def getDf(self, layer):
        """Get attribute table as pandas dataframe.
        
        Args:
            layer (QgsVectorLayer): The vector layer from which to extract features.

        Returns:
            pandas.DataFrame: A DataFrame containing the attributes of the features in the layer.
        """

        # List all columns you want to include in the dataframe. I include all with:
        cols = [f.name() for f in layer.fields()]

        # A generator to yield one row at a time
        datagen = ([f[col] for col in cols] for f in layer.getFeatures())

        return pd.DataFrame(datagen, columns=cols)

    def editAttributeTable(self, df, asset, flood):
        """Edits attribute table to obtain fields that are important for risk statistics exported as Excel.
        
        Args:
            df (DataFrame): DataFrame representing the attribute table.
            asset (str): Type of asset.
            flood (str): Type of flood.

        Returns:
            DataFrame: Modified DataFrame containing selected fields and additional columns for asset type and flood type.
        """

        # Fieldnames to keep
        df = df[["SumVul", "assets"]].copy()
        df.reset_index(drop=True, inplace=True)

        # Add fields and set values
        df["Asset_Type"] = asset
        df["Flood_Type"] = flood
        return df

    def createRiskDataTable(self, data, df, assetType, floodType):
        """Counts assets per flood type and risk and creates table.
        
        Args:
            data (DataFrame): DataFrame containing the data to be analyzed.
            df (DataFrame): DataFrame to which the risk data will be added.
            assetType (str): Type of asset.
            floodType (str): Type of flood.

        Returns:
            DataFrame: Modified DataFrame containing the risk data.
        """

        count = data.groupby(["assets", "SumVul"]).size().reset_index()

        # for row in count.iterrows():
        for row in range(0, count.shape[0]):
            # df.iat[1,2]
            print(count.iat[row, 0])
            d = pd.DataFrame(
                {
                    "Asset_Type": assetType,
                    "Asset": count.iat[row, 0],
                    "Flood_Type": floodType,
                    "Risk": count.iat[row, 1],
                    "Count": count.iat[row, 2],
                },
                index=[1],
            )
            df = pd.concat([df, d], ignore_index=True)

        return df

    def removePdfFiles(self, folder_path):
        """Remove PDF files from a specified directory.

        Args:
            folder_path (str): The path to the directory containing the PDF files.
        """

        # Iterate over the files in the specified directory
        for filename in os.listdir(folder_path):
            # Check if the file has a ".pdf" extension
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(folder_path, filename)

                os.remove(file_path)

    def openLayout(self, layout):

        self.layoutDesigner = self.iface.openLayoutDesigner(layout)

        if self.layoutDesigner:
            self.waitForClosure(self.layoutDesigner)

    def waitForClosure(self, designer_interface):
        # Create an event loop to block execution
        self.event_loop = QEventLoop()
        designer_interface.destroyed.connect(self.closeEvent)
        self.event_loop.exec_()

    def closeEvent(self):
        print("Layout Designer closed. Resuming execution.")
        if self.event_loop:
            self.event_loop.quit()

    
