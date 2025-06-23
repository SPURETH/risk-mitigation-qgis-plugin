# -*- coding: utf-8 -*-

import os
from .UNHCR_generalFunctions import GeneralFunctions
from .UNHCR_dialog_layoutManager import LayoutManager

from qgis.core import QgsProject, QgsEditFormConfig, QgsTextFormat, QgsLayoutItemLabel, QgsLayout
from qgis.core import *
from PyQt5.QtGui import QFont
from qgis import processing
from PyQt5.QtCore import Qt, QDateTime, QEventLoop
from PyQt5.QtXml import QDomDocument

class Step12:
    """This class contains all functions needed to perform step 12."""

    def __init__(self, iface):
        """Constructor."""

        self.iface = iface
        self.generalFunctions = GeneralFunctions(self.iface)
        self.absPath = QgsProject.instance().absolutePath()
        self.layoutManager = QgsProject.instance().layoutManager()

        self._removeLayouts()

    def _removeLayouts(self):
        """Remove previously used layouts."""

        for layout in self.layoutManager.layouts():
            self.layoutManager.removeLayout(layout)

    def setupMap(self, visLayernameList):
        """Setup map layers and visibility.
        
        Args:
            visLayernameList (list of str): List of layer names to be made visible on the map.
        """

        lyrOSM = QgsProject.instance().mapLayersByName("Basemap")[0]

        root = QgsProject.instance().layerTreeRoot()
        allLayers = root.layerOrder()

        for layer in allLayers:
            root.findLayer(layer.id()).setItemVisibilityChecked(False)

            if layer.name() == "temp":
                QgsProject.instance().removeMapLayer(layer.id())

        root.findLayer(lyrOSM).setItemVisibilityChecked(True)

        for layerName in visLayernameList:
            if "Roads" in layerName:
                self.generalFunctions.addLayer(layerName, "LayerStyle_Step10_Line")
            else:
                self.generalFunctions.addLayer(layerName, "LayerStyle_Step10_Polygon")

            mapLayer = QgsProject.instance().mapLayersByName(layerName)[0]
            root.findLayer(mapLayer).setItemVisibilityChecked(True)

    def openLayout(self, layoutPath):

        layout = QgsPrintLayout(QgsProject.instance())
        
        # Read the template file as a QDomDocument (XML)
        doc = QDomDocument()
        with open(layoutPath, 'r') as template_file:
            template_content = template_file.read()

        # Set the string content to the QDomDocument
        doc.setContent(template_content)

        # Load the template into the layout
        context = QgsReadWriteContext()
        layout.loadFromTemplate(doc, context)

        ## Set current map extent
        # Get the layer named "SettlementArea"
        campArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        campExtent = campArea.extent()

        # Add buffer to the extent
        buffer_distance = 0.002  # Buffer distance in map units
        bufferedExtent = QgsRectangle(
            campExtent.xMinimum() - buffer_distance,
            campExtent.yMinimum() - buffer_distance,
            campExtent.xMaximum() + buffer_distance,
            campExtent.yMaximum() + buffer_distance,
        )

        # Find the map item in the layout
        for item in layout.items():
            if isinstance(item, QgsLayoutItemMap):
                # Set the buffered extent
                item.setExtent(bufferedExtent)
                # Resize the map item to fit within the paper
                item.attemptResize(QgsLayoutSize(230, 178, QgsUnitTypes.LayoutMillimeters))
                item.refresh()  # Apply the changes
                break  # Exit the loop after modifying the first map item


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

    def exportLayoutAsPDF(self, layoutName, titleText, exportName):
        """Setup print layout and export it as PDF file.
        
        Args:
            layoutName (str): Name to be given to the layout.
            titleText (str): Title to be added to the PDF.
            exportName (str): Name of the PDF file to be exported.
        """

        layout = QgsPrintLayout(QgsProject.instance())

        # initializes default settings for blank print layout canvas
        layout.initializeDefaults()

        layout.setName(layoutName)
        self.layoutManager.addLayout(layout)

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

        # title
        title = QgsLayoutItemLabel(layout)
        title.setText(titleText)

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

        # date
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

        # scale
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

        # this accesses a specific layout, by name (which is a string)
        layout = self.layoutManager.layoutByName(layoutName)

        # this creates a QgsLayoutExporter object
        exporter = QgsLayoutExporter(layout)

        # this exports a pdf of the layout object
        exportPath = self.absPath + "/" + exportName + ".pdf"
        exporter.exportToPdf(exportPath, QgsLayoutExporter.PdfExportSettings())

    def exportLayoutAsPDFusingTemplate(self, layoutPath, exportName):

        layout = QgsPrintLayout(QgsProject.instance())
        
        # Read the template file as a QDomDocument (XML)
        doc = QDomDocument()
        with open(layoutPath, 'r') as template_file:
            template_content = template_file.read()

        # Set the string content to the QDomDocument
        doc.setContent(template_content)

        # Load the template into the layout
        context = QgsReadWriteContext()
        layout.loadFromTemplate(doc, context)

        ## Set current map extent
        # Get the layer named "SettlementArea"
        campArea = QgsProject.instance().mapLayersByName("SettlementArea")[0]
        campExtent = campArea.extent()

        # Add buffer to the extent
        buffer_distance = 0.002  # Buffer distance in map units
        bufferedExtent = QgsRectangle(
            campExtent.xMinimum() - buffer_distance,
            campExtent.yMinimum() - buffer_distance,
            campExtent.xMaximum() + buffer_distance,
            campExtent.yMaximum() + buffer_distance,
        )

        # Find the map item in the layout
        for item in layout.items():
            if isinstance(item, QgsLayoutItemMap):
                # Set the buffered extent
                item.setExtent(bufferedExtent)
                # Resize the map item to fit within the paper
                item.attemptResize(QgsLayoutSize(230, 178, QgsUnitTypes.LayoutMillimeters))
                item.refresh()  # Apply the changes
                break  # Exit the loop after modifying the first map item

        # this creates a QgsLayoutExporter object
        exporter = QgsLayoutExporter(layout)

        # this exports a pdf of the layout object
        exportPath = self.absPath + "/" + exportName + ".pdf"
        exporter.exportToPdf(exportPath, QgsLayoutExporter.PdfExportSettings())

    #def _findMapExtent():
