# -*- coding: utf-8 -*-


import shutil
import pathlib
import sys
import os

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QDialog
from qgis.core import QgsProject, QgsEditFormConfig, QgsFeatureRequest, QgsLayerTreeLayer
from qgis.utils import iface

from qgis.core import *  # attach main QGIS library
from qgis.utils import *  # attach main python library

from qgis.core import QgsProject, Qgis, QgsVectorFileWriter

# used to install dependencies
from .installer import installer_func

installer_func()

import pandas as pd
import numpy as np

# Print the filepath of the pandas module
print(f"pandas is loaded from: {pd.__file__}")
print(f"numpy is loaded from: {np.__file__}")

from functools import reduce

#

from qgis.PyQt.QtXml import QDomDocument

import time
from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *

from qgis.PyQt.QtWidgets import QMessageBox, QMenu, QToolButton

from PyQt5.QtGui import (
    QImage,
    QIcon,
    QPixmap,
    QPalette,
    QBrush,
    QColor,
    QFontDatabase,
    QFont,
)

from osgeo import gdal
from qgis.core import *

import processing

from qgis.gui import QgsAttributeTableView

# Initialize Qt resources from file resources.py
from .resources import *

from .UNHCR_step1 import Step1
from .UNHCR_step2 import Step2
from .UNHCR_step3 import Step3
from .UNHCR_step4 import Step4
from .UNHCR_step5 import Step5
from .UNHCR_step6 import Step6
from .UNHCR_step7 import Step7
from .UNHCR_step8 import Step8
from .UNHCR_step9 import Step9
from .UNHCR_step10 import Step10
from .UNHCR_step11 import Step11
from .UNHCR_step12 import Step12
from .UNHCR_step13 import Step13
from .UNHCR_step14 import Step14

from .UNHCR_generalFunctions import GeneralFunctions

from .UNHCR_dialog_message import MessageDialog
from .UNHCR_dialog_message_yesno import MessageDialogYesNo
from .UNHCR_dialog_dataUpload import DataUploadDialog
from .UNHCR_dialog_dataUploadRF import DataUploadRFDialog
from .UNHCR_dialog_chooseOption import ChooseOptionDialog
from .UNHCR_dialog_attributeTable import AttributeTableDialog
from .UNHCR_dialog_floodAdjustment import FloodAdjustmentDialog
from .UNHCR_dialog_floodAdjustmentPluvial import FloodAdjustmentPluvialDialog
from .UNHCR_dialog_buildings import BuildingsDialog
from .UNHCR_dialog_infrastructure import InfrastructureDialog
from .UNHCR_dialog_riskAdjustment import RiskAdjustmentDialog
from .UNHCR_dialog_checkMeasures import CheckMeasuresDialog
from .UNHCR_dialog_errorMessage import ErrorMessageDialog
from .UNHCR_dialog_loadingBar import LoadingBar
from .UNHCR_dialog_layoutManager import LayoutManager
from .UNHCR_dialog_fieldPresent import FieldPresentDialog

import os.path

class Main:
    """Main class of the plugin.

    This class represents the overall functionality of the plugin.
    For each step of the plugin there is a function in here.

    """

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface

        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "Main_{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&UNHCR Risk Mapping")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("Main", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    # Change icon & header here!
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # TODO: Add for more icons to other actions
        icon1_path = ":/plugins/UNHCR/icon1.png"
        icon2_path = ":/plugins/UNHCR/icon2.png"
        icon3_path = ":/plugins/UNHCR/icon3.png"
        icon4_path = ":/plugins/UNHCR/icon4.png"
        icon5_path = ":/plugins/UNHCR/icon5.png"
        icon6_path = ":/plugins/UNHCR/icon6.png"
        icon7_path = ":/plugins/UNHCR/icon7.png"
        icon8_path = ":/plugins/UNHCR/icon8.png"
        icon9_path = ":/plugins/UNHCR/icon9.png"
        icon10_path = ":/plugins/UNHCR/icon10.png"
        icon11_path = ":/plugins/UNHCR/icon11.png"
        icon12_path = ":/plugins/UNHCR/icon12.png"
        icon13_path = ":/plugins/UNHCR/icon13.png"
        icon14_path = ":/plugins/UNHCR/icon14.png"

        self.add_action(
            icon1_path,
            text=self.tr("(1) Selection of Basemap and definition of Settlement Extent"),
            callback=self.runStep1,
            parent=self.iface.mainWindow(),
        )

        self.actionRoad = self.add_action(
            icon2_path,
            text=self.tr("Upload Transport Infrastructure  Data"),
            callback=self.runStep2Road,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.actionBuildings = self.add_action(
            icon2_path,
            text=self.tr("Upload Buildings Data"),
            callback=self.runStep2Buildings,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.actionRiverine = self.add_action(
            icon2_path,
            text=self.tr("Upload Riverine Flood Data"),
            callback=self.runStep2Riverine,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.actionPluvial = self.add_action(
            icon2_path,
            text=self.tr("Upload Pluvial Flood Data"),
            callback=self.runStep2Pluvial,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.popupMenu = QMenu(self.iface.mainWindow())

        self.popupMenu.addAction(self.actionRoad)
        self.popupMenu.addAction(self.actionBuildings)
        self.popupMenu.addAction(self.actionRiverine)
        self.popupMenu.addAction(self.actionPluvial)

        self.toolButton = QToolButton()

        self.toolButton.setMenu(self.popupMenu)
        self.toolButton.setDefaultAction(self.actionRoad)
        self.toolButton.setPopupMode(
            QToolButton.InstantPopup
        )

        self.dropAction = self.iface.addToolBarWidget(self.toolButton)

        self.add_action(
            icon3_path,
            text=self.tr("(3) Riverine Flood Adjustment"),
            callback=self.runStep3,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon4_path,
            text=self.tr("(4) Pluvial Flood Adjustment"),
            callback=self.runStep4,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon5_path,
            text=self.tr("(5) Hazard Area Calculation"),
            callback=self.runStep5,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon6_path,
            text=self.tr("(6) Change Buildings"),
            callback=self.runStep6,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon7_path,
            text=self.tr("(7) Add Buildings"),
            callback=self.runStep7,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon8_path,
            text=self.tr("(8) Add Technical Infrastructure"),
            callback=self.runStep8,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon9_path,
            text=self.tr("(9) Add Transport Infrastructure"),
            callback=self.runStep9,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon10_path,
            text=self.tr("(10) Calculate Risk"),
            callback=self.runStep10,
            parent=self.iface.mainWindow(),
        )

        self.add_action(
            icon11_path,
            text=self.tr("(11) Adjust Risk"),
            callback=self.runStep11,
            parent=self.iface.mainWindow(),
        )

        # self.add_action(
        #     icon12_path,
        #     text=self.tr("(12) Export Risk Map"),
        #     callback=self.runStep12,
        #     parent=self.iface.mainWindow(),
        # )

        self.actionPrintPluvial = self.add_action(
            icon12_path,
            text=self.tr("Export Pluvial Risk Map"),
            callback=self.runStep12Pluvial,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.actionPrintRiverine = self.add_action(
            icon12_path,
            text=self.tr("Export Riverine Risk Map"),
            callback=self.runStep12Riverine,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.popupMenu12 = QMenu(self.iface.mainWindow())

        self.popupMenu12.addAction(self.actionPrintRiverine)
        self.popupMenu12.addAction(self.actionPrintPluvial)

        self.toolButton12 = QToolButton()

        self.toolButton12.setMenu(self.popupMenu12)
        self.toolButton12.setDefaultAction(self.actionPrintRiverine)
        self.toolButton12.setPopupMode(
            QToolButton.InstantPopup
        )

        self.dropAction12 = self.iface.addToolBarWidget(self.toolButton12)

        self.add_action(
            icon13_path,
            text=self.tr("(13) Choose Measures"),
            callback=self.runStep13,
            parent=self.iface.mainWindow(),
        )

        # self.add_action(
        #     icon14_path,
        #     text=self.tr("(14) Export Mitigation Actions"),
        #     callback=self.runStep14,
        #     parent=self.iface.mainWindow(),
        # )

        self.action14RiverineRoad = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Riverine-Roads"),
            callback=self.runStep14RiverineRoad,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14RiverineBuilding = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Riverine-Buildings"),
            callback=self.runStep14RiverineBuilding,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14RiverineBuilding = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Riverine-Buildings"),
            callback=self.runStep14RiverineBuilding,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14RiverineInfrastrucutre = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Riverine-Technical Infrastrucutre"),
            callback=self.runStep14RiverineInfrastructure,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14PluvialRoad = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Pluvial-Roads"),
            callback=self.runStep14PluvialRoad,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14PluvialBuilding = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Pluvial-Buildings"),
            callback=self.runStep14PluvialBuilding,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14PluvialInfrastrucutre = self.add_action(
            icon14_path,
            text=self.tr("Export Mitigation Actions for Pluival-TechnicalInfrastrucutre"),
            callback=self.runStep14PluvialInfrastructure,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.action14RiskStats = self.add_action(
            icon14_path,
            text=self.tr("Export Risk Statistics"),
            callback=self.runStep14RiskStats,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False,
        )

        self.popupMenu14 = QMenu(self.iface.mainWindow())

        self.popupMenu14.addAction(self.action14RiverineRoad)
        self.popupMenu14.addAction(self.action14RiverineBuilding)
        self.popupMenu14.addAction(self.action14RiverineInfrastrucutre)
        self.popupMenu14.addAction(self.action14PluvialRoad)
        self.popupMenu14.addAction(self.action14PluvialBuilding)
        self.popupMenu14.addAction(self.action14PluvialInfrastrucutre)
        self.popupMenu14.addAction(self.action14RiskStats)

        self.toolButton14 = QToolButton()

        self.toolButton14.setMenu(self.popupMenu14)
        self.toolButton14.setDefaultAction(self.action14RiverineRoad)
        self.toolButton14.setPopupMode(
            QToolButton.InstantPopup
        )

        self.dropAction14 = self.iface.addToolBarWidget(self.toolButton14)

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&UNHCR Risk Mapping"), action)
            self.iface.removeToolBarIcon(action)

        self.iface.removeToolBarIcon(self.dropAction)
        self.iface.removeToolBarIcon(self.dropAction12)
        self.iface.removeToolBarIcon(self.dropAction14)

    def runStep1(self):
        """Step 1: User draws Settlement extent."""

        dlgMessage = MessageDialog()
        dlgMessage1 = MessageDialog()
        dlgMessage2 = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()

        self.generalFunctions = GeneralFunctions(self.iface)

        dlgDataUploadBasemap = DataUploadDialog()

        try:
            self.step1 = Step1(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()
            return
        

        ###

        dlgMessage.setText(
                "Do you want to change the basemap of the project?"
            )

        resultReload = dlgMessage.exec_()

        if resultReload == QDialog.Accepted:
                
            dlgDataUploadBasemap.setText(
                "Select the tif-file for your basemap."
            )
            resultPath = dlgDataUploadBasemap.exec_()

            if resultPath == QDialog.Accepted:

                try:
                    self.generalFunctions.removeLayer("Basemap")
                    filePath = dlgDataUploadBasemap.getFilePath()
                    lyr = self.step1.addRasterLayer(filePath, "Basemap")

                except Exception as e:
                    
                    dlgErrorMessage.setText(
                            "Error: " + str(e), "An unknown error occured."
                        )

                    dlgErrorMessage.exec_()
                    return
                

                QgsProject.instance().addMapLayer(lyr)

                ## move layer to the bottom
                root = QgsProject.instance().layerTreeRoot()
                layerExisting = root.findLayer(lyr)
                layerClone = layerExisting.clone()
                root.addChildNode(layerClone)
                parent = layerExisting.parent()
                parent.removeChildNode(layerExisting)

                # zoom to layer
                self.iface.mapCanvas().setExtent(lyr.extent())
                iface.mapCanvas().refresh()

        if self.step1.layerNotEmpty():

            dlgMessage1.setText(
                "There is already a Settlement Area defined. Do you want to redraw it?"
            )
            result1 = dlgMessage1.exec_()

            if result1 == QDialog.Accepted:
                self.step1.deleteCampArea()

                dlgMessage2.setText(
                    "Please draw the extent of your Settlement or the "
                    "area you would like to analyze. Left click for edge points, right click for finishing.\n\n"
                    "IMPORTANT: Make sure you have selected (highlighted) "
                    "the SettlementArea-Layer in the Layers Window."
                )
                result2 = dlgMessage2.exec_()

                if result2 == QDialog.Accepted:
                    self.step1.drawCamp()

        else:

            dlgMessage2.setText(
                "Please draw the extent of your settlement or the "
                "area you would like to analyze. Left Click for edge points, right click for finishing.\n\n"
                "IMPORTANT: Make sure you have selected (highlighted) "
                "the SettlementArea-Layer in the Layers Window."
            )
            result2 = dlgMessage2.exec_()

            if result2 == QDialog.Accepted:
                self.step1.drawCamp()

    def runStep2Road(self):
        """Step 2: Upload Road Data."""

        self.generalFunctions = GeneralFunctions(self.iface)

        step2Road = Step2(self.iface)

        self.generalFunctions.removeLayer("Roads")

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        dlgDataUploadRoad = DataUploadDialog()

        uploadRoad = True
        if step2Road.filePresent("Roads") and not self.generalFunctions.isLayerEmpty("Roads"):
            uploadRoad = False
            dlgMessage.setText(
                "There is already a Road shp-file. Do you want to reload new data?"
            )
            resultReload = dlgMessage.exec_()

            if resultReload == QDialog.Accepted:
                uploadRoad = True

        if uploadRoad == True:

            dlgDataUploadRoad.setText(
                "To upload tranport infrastructre data select the appropriate shp-file."
            )
            resultPath = dlgDataUploadRoad.exec_()

            if resultPath == QDialog.Accepted:

                try:
                    filePath = dlgDataUploadRoad.getFilePath()
                    lyr = self.generalFunctions.getVectorLayer(
                        filePath, "Roads"
                    )

                except QgsProcessingException as e:
                    dlgErrorMessage.setText(
                        "Error: " + str(e) + ".",
                        "You have probably selected an incorrect file.",
                    )
                    dlgErrorMessage.exec_()
                    return

                lyrClip = self.generalFunctions.clipCampArea(lyr)

                if step2Road.filePresent("Roads"):
                    step2Road.mergeTemplate(lyrClip, "Roads", "temp")
                    step2Road.exchangeShpFile("tempRoads", "Roads")
                    self.generalFunctions.removeShpFile("tempRoads")

                else:
                    step2Road.mergeTemplate(lyrClip, "Roads")

        if step2Road.filePresent("Roads"):
            self.generalFunctions.addLayer("Roads", "LayerStyle_Roads_step2")

    def runStep2Buildings(self):
        """Step 2: Upload Buildings Data."""

        self.generalFunctions = GeneralFunctions(self.iface)
        step2Buildings = Step2(self.iface)
        self.generalFunctions.removeLayer("Buildings")

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        dlgDataUploadBuilding = DataUploadDialog()
        dlgDataChooseBuilding = ChooseOptionDialog(["Vector data (shp)", "Delimited text layer (csv)"])

        uploadBuildings = True
        if step2Buildings.filePresent("Buildings") and not self.generalFunctions.isLayerEmpty("Buildings"):
            uploadBuildings = False
            dlgMessage.setText(
                "There is already a Buildings shp-file. Do you want to reload new data?"
            )
            resultReload = dlgMessage.exec_()

            if resultReload == QDialog.Accepted:
                uploadBuildings = True

        if uploadBuildings == True:

            dlgDataChooseBuilding.setText(
                "Choose the data type of the building data you want to upload."
            )
            resultDataChoose = dlgDataChooseBuilding.exec_()

            if resultDataChoose == QDialog.Accepted:

                if dlgDataChooseBuilding.chosenOption() == "Delimited text layer (csv)":
                    dlgDataUploadBuilding.setText(
                        "Select the csv-file that contains the building data."
                    )

                else:
                    dlgDataUploadBuilding.setText(
                        "Select the shp-file that contains the building data."
                    )

                resultPath = dlgDataUploadBuilding.exec_()

                if resultPath == QDialog.Accepted:

                    self.loadingBar = LoadingBar("Uploading...")

                    def upload():

                        try:
                            filePath = dlgDataUploadBuilding.getFilePath()

                            if dlgDataChooseBuilding.chosenOption() == "Delimited text layer (csv)":

                                lyr = step2Buildings.addDelimitedLayer(
                                    filePath, "Buildings"
                                )

                            else:
                                lyr = self.generalFunctions.getVectorLayer(
                                    filePath, "Buildings"
                                )

                        except QgsProcessingException as e:
                            if "Could not load source layer for INPUT_A" in str(e):
                                dlgErrorMessage.setText(
                                    "Error: " + str(e),
                                    "You might have selected an incorrect file.",
                                )
                            else:
                                dlgErrorMessage.setText(
                                    "Error: " + str(e), "An unknown error occured."
                                )

                            self.loadingBar.close()
                            dlgErrorMessage.exec_()
                            return

                        lyrClip = self.generalFunctions.clipCampArea(lyr)

                        return lyrClip

                    self.loadingBar.upload_file_operation(uploadFunction=upload)

                    lyrClip = self.loadingBar.result

                    if lyrClip == None:
                        return

                    if step2Buildings.filePresent("Buildings"):
                        step2Buildings.mergeTemplate(lyrClip, "Buildings", "temp")
                        step2Buildings.exchangeShpFile("tempBuildings", "Buildings")
                        self.generalFunctions.removeShpFile("tempBuildings")

                    else:
                        step2Buildings.mergeTemplate(lyrClip, "Buildings")

        if step2Buildings.filePresent("Buildings"):
            self.generalFunctions.addLayer("Buildings", "LayerStyle_Buildings_step2")

    def runStep2Riverine(self):
        """Step 2: Upload Riverine flood Data."""

        self.generalFunctions = GeneralFunctions(self.iface)
        step2Riverine = Step2(self.iface)
        self.generalFunctions.removeLayer("RiverineFlood")

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        dlgDataUploadRiverineLocal = DataUploadDialog()
        dlgDataUploadRiverineGlobal = DataUploadRFDialog()
        dlgDataChooseRiverine = ChooseOptionDialog(["Vector data (shp)", "Raster data (tif)"])

        uploadRiverine = True
        if step2Riverine.filePresent("RiverineFlood") and not self.generalFunctions.isLayerEmpty("RiverineFlood"):
            uploadRiverine = False
            dlgMessage.setText(
                "There is already a RiverineFlood shp-file. Do you want to reload new data?"
            )
            resultReload = dlgMessage.exec_()

            if resultReload == QDialog.Accepted:
                uploadRiverine = True

        if uploadRiverine == True:

            dlgDataChooseRiverine.setText(
                "Choose the data type of the riverine flood data you want to upload."
            )
            resultDataChoose = dlgDataChooseRiverine.exec_()

            if resultDataChoose == QDialog.Accepted:

                if dlgDataChooseRiverine.chosenOption() == "Raster data (tif)":
                    resultPath = dlgDataUploadRiverineGlobal.exec_()

                else:
                    dlgDataUploadRiverineLocal.setText(
                        "Select the shp-file that contains your riverine flood data."
                    )
                    resultPath = dlgDataUploadRiverineLocal.exec_()

                if resultPath == QDialog.Accepted:

                    if dlgDataChooseRiverine.chosenOption() == "Raster data (tif)":

                        self.loadingBar = LoadingBar("Uploading...")

                        def upload():
                            try:
                                lyrRiverine_10 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_10.filePath(), "10"
                                )
                                lyrRiverine_20 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_20.filePath(), "20"
                                )
                                lyrRiverine_50 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_50.filePath(), "50"
                                )
                                lyrRiverine_100 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_100.filePath(), "100"
                                )
                                lyrRiverine_200 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_200.filePath(), "200"
                                )
                                lyrRiverine_500 = step2Riverine.prepRiverineFlood(
                                    dlgDataUploadRiverineGlobal.FW_500.filePath(), "500"
                                )

                            except QgsProcessingException as e:
                                if "Could not load source layer for INPUT_A" in str(e):
                                    dlgErrorMessage.setText(
                                        "Error: " + str(e),
                                        "You might have selected an incorrect file.",
                                    )
                                else:
                                    dlgErrorMessage.setText(
                                        "Error: " + str(e), "An unknown error occured."
                                    )

                                self.loadingBar.close()
                                dlgErrorMessage.exec_()

                                return

                            lyrRiverine = processing.run(
                                "qgis:mergevectorlayers",
                                {
                                    "LAYERS": [
                                        lyrRiverine_10,
                                        lyrRiverine_20,
                                        lyrRiverine_50,
                                        lyrRiverine_100,
                                        lyrRiverine_200,
                                        lyrRiverine_500,
                                    ],
                                    "CRS": "EPSG:4326",
                                    "OUTPUT": "memory:",
                                },
                            )["OUTPUT"]

                            return lyrRiverine

                        self.loadingBar.upload_file_operation(uploadFunction=upload)
                        lyrRiverine = self.loadingBar.result

                        # rename gridcode to WaterHeight
                        lyrRiverine.startEditing()
                        field_index = lyrRiverine.fields().indexOf('gridcode')
                        lyrRiverine.renameAttribute(field_index, 'WaterHgt')
                        lyrRiverine.commitChanges()

                        #lyrStyle = "LayerStyle_Flood"

                        if lyrRiverine == None:
                            return

                    else:

                        ## upload file

                        try:
                            filePath = dlgDataUploadRiverineLocal.getFilePath()
                            lyr = self.generalFunctions.getVectorLayer(
                                filePath, "RiverineFlood"
                            )
                            lyrRiverine = lyr.clone()
                            # lyrRiverine = step2Riverine.mergeTemplateReturn(
                            #     lyr, "FloodRiverine"
                            # )

                            lyrRiverine = processing.run(
                                "qgis:fixgeometries",
                                {
                                    "INPUT": lyrRiverine,
                                    "OUTPUT": "memory:"  # Output a fixed layer to memory
                                }
                            )["OUTPUT"]

                            # invalid_features = []
                            # for feature in lyrRiverine.getFeatures():
                            #     if not feature.geometry().isGeosValid():
                            #         invalid_features.append(feature.id())
                            # print(invalid_features)

                        except QgsProcessingException as e:
                            if "Could not load source layer for INPUT_A" in str(e):
                                dlgErrorMessage.setText(
                                    "Error: " + str(e),
                                    "You might have selected an incorrect file.",
                                )
                            else:
                                dlgErrorMessage.setText(
                                    "Error: " + str(e), "An unknown error occured."
                                )

                            dlgErrorMessage.exec_()
                            return

                        ## is a column that resembles hazard already present

                        #fieldExisting = False

                        dlgMessage.setText(
                            "Is there already a field present represeting the Hazard value?"
                        )
                        resultField = dlgMessage.exec_()

                        if resultField == QDialog.Accepted:

                            message = (
                                "Please select the field you would like to designate as the 'Hazard' field. \n"
                            )

                            dlgFieldPresent = FieldPresentDialog(message, lyrRiverine)

                            result = dlgFieldPresent.exec_()

                            if result == QDialog.Accepted:

                                #fieldExisting = True

                                field = dlgFieldPresent.getField()

                                # rename field to hazard
                                lyrRiverine.startEditing()
                                field_index = lyrRiverine.fields().indexOf(field)
                                lyrRiverine.renameAttribute(field_index, 'Hazard')
                                lyrRiverine.commitChanges()

                                editable_layers = ["Hazard"]

                                #lyrStyle = "LayerStyle_FloodRisk"

                            else:
                                return

                        # no:
                        else:

                            # lyrRiverine = step2Riverine.mergeTemplateReturn(
                            #     lyrRiverine, "FloodRiverine"
                            # )
                            
                            fields = {
                                "WaterHgt": QVariant.Int,
                                "Intensity": QVariant.Int,
                                "RepeatYear": QVariant.Int,
                                "Hazard": QVariant.Int,
                            }

                            step2Riverine.addFields(lyrRiverine, fields)

                            editable_layers = ["WaterHgt", "RepeatYear"]

                            #lyrStyle = "LayerStyle_Flood"

                        step2Riverine.setLayerStyle(
                            lyrRiverine, "/LayerStyle_LocalFloodTemp.qml"
                        )
                        QgsProject.instance().addMapLayer(lyrRiverine)

                        # fill in WaterHgt and RepeatYear!
                        dlgAttributeTable = AttributeTableDialog(
                            iface.mainWindow(), iface.mapCanvas(), lyrRiverine, editable_layers
                        )
                        dlgAttributeTable.exec_()

                    lyrRiverineClip = step2Riverine.clipCampArea(lyrRiverine)

                    if lyrRiverineClip.fields().indexOf("Intensity") != -1:
                        step2Riverine.calculateFloodIntensity(lyrRiverineClip, "riverine")  # return?

                    if step2Riverine.filePresent("RiverineFlood"):
                        step2Riverine.writeVectorLayer(
                            lyrRiverineClip, "/tempRiverineFlood.shp"
                        )
                        step2Riverine.exchangeShpFile(
                            "tempRiverineFlood", "RiverineFlood"
                        )
                        self.generalFunctions.removeShpFile("tempRiverineFlood")

                    else:
                        step2Riverine.writeVectorLayer(
                            lyrRiverineClip, "/RiverineFlood.shp"
                        )

                    step2Riverine.removeLayer("output")

        if step2Riverine.filePresent("RiverineFlood") and not self.generalFunctions.isLayerEmpty("RiverineFlood"):

            if self.generalFunctions.fieldsExist("RiverineFlood", ["Intensity"]):
                self.generalFunctions.addLayer("RiverineFlood", "LayerStyle_Flood")
            else:
                self.generalFunctions.addLayer("RiverineFlood", "LayerStyle_FloodRisk")

    def runStep2Pluvial(self):
        """Step 2: Upload riverine flood Data."""

        self.generalFunctions = GeneralFunctions(self.iface)
        step2Pluv = Step2(self.iface)
        self.generalFunctions.removeLayer("PluvialFlood")
        self.absPath = (
            QgsProject.instance().absolutePath()
        )

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        dlgDataUploadPluvial = DataUploadDialog()

        uploadPluvial = True
        if step2Pluv.filePresent(
            "PluvialFlood"
        ) and not self.generalFunctions.isLayerEmpty("PluvialFlood"):
            uploadPluvial = False
            dlgMessage.setText(
                "There is already a PluvialFlood shp-file. Do you want to reload new data?"
            )
            resultReload = dlgMessage.exec_()

            if resultReload == QDialog.Accepted:
                uploadPluvial = True

        if uploadPluvial == True:

            dlgDataUploadPluvial.setText(
                "Select the shp-file of your local pluvial flood data."
            )
            resultPath = dlgDataUploadPluvial.exec_()

            if resultPath == QDialog.Accepted:

                try:
                    filePath = dlgDataUploadPluvial.getFilePath()
                    lyr = step2Pluv.addVectorLayer(filePath, "PluvialFlood")
                    lyrPluvial = lyr.clone()
                    #lyrPluvial = step2Pluv.mergeTemplateReturn(lyr, "FloodLocal")



                    # if step2Pluv.filePresent("PluvialFlood"):
                    #     step2Pluv.writeVectorLayer(lyr, "/tempPluvialFlood.shp")
                    #     step2Pluv.exchangeShpFile("tempPluvialFlood", "PluvialFlood")
                    #     self.generalFunctions.removeShpFile("tempPluvialFlood")

                    # else:
                    #     step2Pluv.writeVectorLayer(lyr, "/PluvialFlood.shp")
                    
                    # lyrPluvial = step2Pluv.addVectorLayer(self.absPath + "/PluvialFlood.shp", "PluvialFlood")

                    lyrPluvial = processing.run(
                                "qgis:fixgeometries",
                                {
                                    "INPUT": lyrPluvial,
                                    "OUTPUT": "memory:"  # Output a fixed layer to memory
                                }
                            )["OUTPUT"]

                except QgsProcessingException as e:
                    if "Could not load source layer for INPUT_A" in str(e):
                        dlgErrorMessage.setText(
                            "Error: " + str(e),
                            "You might have selected an incorrect file.",
                        )
                    else:
                        dlgErrorMessage.setText(
                            "Error: " + str(e), "An unknown error occured."
                        )

                    dlgErrorMessage.exec_()
                    return

                ## is a column present that resembles intensity
                dlgMessage.setText(
                            "Is there already a field present represeting the Intensity value?"
                        )
                resultField = dlgMessage.exec_()

                if resultField == QDialog.Accepted:

                    message = (
                        "Please select the field you would like to designate as the 'Intensity' field. \n"
                    )

                    dlgFieldPresent = FieldPresentDialog(message, lyrPluvial)

                    result = dlgFieldPresent.exec_()

                    if result == QDialog.Accepted:

                        #fieldExisting = True

                        field = dlgFieldPresent.getField()

                        # rename field to hazard
                        lyrPluvial.startEditing()
                        field_index = lyrPluvial.fields().indexOf(field)
                        lyrPluvial.renameAttribute(field_index, 'Intensity')
                        lyrPluvial.commitChanges()

                        #editable_layers = ["Intensity", "YrlyFlood"]

                    else:
                        return
                
                #else:

                    #lyrPluvial = step2Pluv.mergeTemplateReturn(lyrPluvial, "FloodPluvial")

                    #editable_layers = ["Intensity", "YrlyFlood"]

                fields = {
                    "Intensity": QVariant.Int,
                    "YrlyFlood": QVariant.Bool,
                    "Hazard": QVariant.Int,
                }

                step2Pluv.addFields(lyrPluvial, fields)
                editable_layers = ["Intensity", "YrlyFlood"]

                step2Pluv.setLayerStyle(lyrPluvial, "/LayerStyle_LocalFloodTemp.qml")
                QgsProject.instance().addMapLayer(lyrPluvial)

                # ## restrict YrlyFlood to 0 and 1
                # fieldIndex = lyrPluvial.fields().indexFromName('YrlyFlood')
                # editor_widget_setup = QgsEditorWidgetSetup( 'ValueMap', {
                #                         'map': {'Description 1': 0, 
                #                                 'Description 2': 1}
                #                         }
                #                     )
                # #editor_widget_setup = QgsEditorWidgetSetup('CheckBox', {})
                # lyrPluvial.setEditorWidgetSetup(fieldIndex, editor_widget_setup)

                # lyrPluvial.triggerRepaint()
                # ##

                #self.iface.showAttributeTable(lyrPluvial)

                # fill in WaterHgt and RepeatYear!
                dlgAttributeTable = AttributeTableDialog(
                    iface.mainWindow(), iface.mapCanvas(), lyrPluvial, editable_layers
                )
                dlgAttributeTable.exec_()

                lyrPluvialClip = step2Pluv.clipCampArea(lyrPluvial)
                #step2Pluv.calculateFloodIntensity(lyrPluvialClip, "pluvial")  # return?

                step2Pluv.checkForNullValue(lyrPluvialClip, "Intensity", 99)
                step2Pluv.checkForNullValue(lyrPluvialClip, "YrlyFlood", 0)

                if step2Pluv.filePresent("PluvialFlood"):
                    step2Pluv.writeVectorLayer(lyrPluvialClip, "/tempPluvialFlood.shp")
                    step2Pluv.exchangeShpFile("tempPluvialFlood", "PluvialFlood")
                    self.generalFunctions.removeShpFile("tempPluvialFlood")

                else:
                    step2Pluv.writeVectorLayer(lyrPluvialClip, "/PluvialFlood.shp")

                step2Pluv.removeLayer("output")

        if step2Pluv.filePresent(
            "PluvialFlood"
        ) and not self.generalFunctions.isLayerEmpty("PluvialFlood"):
            self.generalFunctions.addLayer("PluvialFlood", "LayerStyle_Flood")


    def runStep3(self):
        """Step 3: Riverine Adjustment incl. Changing Return Period and Intensity."""

        message = (
            "If you want to add more zones prone to riverine floods manually, "
            "please choose the return period and intensity level of the flood"
            "event in the to be drawn area. After pressing OK, you can "
            "draw the extent of the area affected. \n\nIMPORTANT: Make sure you have selected (highlighted) the "
            "RiverineFlood Layer in the Layers Window.\n\n"
            "You can add several flood prone zones by repeating this step (button 3)."
        )

        self.dlgFloodAdjustment = FloodAdjustmentDialog(message)
        dlgErrorMessage = ErrorMessageDialog()

        try:
            self.step3 = Step3(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()

            return

        result = self.dlgFloodAdjustment.exec_()

        if result == QDialog.Accepted:

            returnPeriod = self.dlgFloodAdjustment.getReturnPeriod()
            intenstiy = self.dlgFloodAdjustment.getInsentity()

            self.step3.adjustFlood(intenstiy, returnPeriod)

    def runStep4(self):
        """Step 4: Pluvial Adjustment incl. Return Period and Intensity"""

        message = (
            "If you want to add more zones prone to pluvial floods manually, "
            "please choose the intensity level of the flood "
            "event in the to be drawn area. After pressing OK, you can "
            "draw the extent of the area affected. \n\nIMPORTANT: Make sure you have selected (highlighted) the "
            "PluvialFlood Layer in the Layers Window.\n\n"
            "You can add several flood prone zones by repeating this step (button 4)."
        )

        self.dlgFloodAdjustment = FloodAdjustmentPluvialDialog(message)

        dlgErrorMessage = ErrorMessageDialog()

        try:
            self.step4 = Step4(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()
            return

        result = self.dlgFloodAdjustment.exec_()

        if result == QDialog.Accepted:

            intenstiy = self.dlgFloodAdjustment.getInsentity()

            self.step4.adjustFlood(intenstiy)

    def runStep5(self):
        """Step 5: Calculate Hazard Area, Calculate Riskintensity & Clip all Layers to Hazard Area."""

        self.generalFunctions = GeneralFunctions(self.iface)
        step5 = Step5(self.iface)
        self.absPath = (
            QgsProject.instance().absolutePath()
        )

        ###

        dlgErrorMessage = ErrorMessageDialog()

        try:

            BUILDINGS = self.generalFunctions.isLayerEmpty("Buildings")
            ROADS = self.generalFunctions.isLayerEmpty("Roads")
            PLUVIAL = self.generalFunctions.isLayerEmpty("PluvialFlood")
            RIVERINE = self.generalFunctions.isLayerEmpty("RiverineFlood")
            
            if  BUILDINGS and ROADS or PLUVIAL and RIVERINE:

                raise FileExistsError("Data upload incomplete")

        except Exception as e:
            
            dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "Please upload at least one infrastructure layer (buildings or roads) and one flood layer (pluvial or riverine) to proceed.",
                )

            dlgErrorMessage.exec_()

            return
    
        ###

        self.generalFunctions.removeLayer("RiverineFlood_Clip")
        self.generalFunctions.removeLayer("PluvialFlood_Clip")
        self.generalFunctions.removeLayer("HazardArea")
        self.generalFunctions.removeLayer("Buildings_Clip")
        self.generalFunctions.removeLayer("Roads_Clip")
        self.generalFunctions.removeLayer("TechnicalInfrastructure_Clip")

        dlgMessage = MessageDialog()

        if self.generalFunctions.filePresent("HazardArea"):
            dlgMessage.setText(
                "In this step, the hazard area will be calculated. It may take some time; please do not interrupt.\n\n"
                "You have already calculated the hazard area. Do you want to recalculate it?"
            )

        else:
            dlgMessage.setText(
                "In this step, the hazard area will be calculated here. It may take some time; please do not interrupt."
            )

        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            # clip Flood to Camp Area
            lyrRiverineFloodClip = self.generalFunctions.clipCampArea(
                self.absPath + "/RiverineFlood.shp"
            )
            lyrPluvialFloodClip = self.generalFunctions.clipCampArea(
                self.absPath + "/PluvialFlood.shp"
            )

            if self.generalFunctions.fieldsExist("RiverineFlood", ["RepeatYear", "WaterHgt"]):
                step5.calculateHazard(lyrRiverineFloodClip, "riverine")

            step5.calculateHazard(lyrPluvialFloodClip, "pluvial")

            lyrHazardArea = processing.run(
                "qgis:mergevectorlayers",
                {
                    "LAYERS": [lyrRiverineFloodClip, lyrPluvialFloodClip],
                    "CRS": "EPSG:4326",
                    "OUTPUT": "memory:",
                },
            )["OUTPUT"]

            lyrInfrastructure = QgsVectorLayer(
                self.absPath + "/" + "TechnicalInfrastructure" + ".shp",
                "TechnicalInfrastructure",
                "ogr",
            )
            lyrInfrastructureClip = self.generalFunctions.extractByLocation(
                lyrInfrastructure, lyrHazardArea
            )

            lyrRoads = QgsVectorLayer(
                self.absPath + "/" + "Roads" + ".shp", "Roads", "ogr"
            )
            lyrRoadsClip = self.generalFunctions.extractByLocation(
                lyrRoads, lyrHazardArea
            )

            lyrBuildings = QgsVectorLayer(
                self.absPath + "/" + "Buildings" + ".shp", "Buildings", "ogr"
            )
            lyrBuildingsClip = self.generalFunctions.extractByLocation(
                lyrBuildings, lyrHazardArea
            )

            step5.prepRoadData(lyrRoadsClip)
            step5.prepBuildingsData(lyrBuildingsClip)

            # Hazard Area Merge two Floods
            if self.generalFunctions.filePresent("HazardArea"):

                self.generalFunctions.writeTempFile(
                    lyrRiverineFloodClip, "tempRiverineFlood_Clip", "RiverineFlood_Clip"
                )
                self.generalFunctions.writeTempFile(
                    lyrPluvialFloodClip, "tempPluvialFlood_Clip", "PluvialFlood_Clip"
                )
                self.generalFunctions.writeTempFile(
                    lyrHazardArea, "tempHazardArea", "HazardArea"
                )
                self.generalFunctions.writeTempFile(
                    lyrInfrastructureClip,
                    "tempInfrastructure_Clip",
                    "TechnicalInfrastructure_Clip",
                )
                self.generalFunctions.writeTempFile(
                    lyrRoadsClip, "tempRoads_Clip", "Roads_Clip"
                )
                self.generalFunctions.writeTempFile(
                    lyrBuildingsClip, "tempBuildings_Clip", "Buildings_Clip"
                )

            else:

                self.generalFunctions.writeVectorLayer(
                    lyrRiverineFloodClip, "RiverineFlood_Clip"
                )
                self.generalFunctions.writeVectorLayer(
                    lyrPluvialFloodClip, "PluvialFlood_Clip"
                )
                self.generalFunctions.writeVectorLayer(lyrHazardArea, "HazardArea")
                self.generalFunctions.writeVectorLayer(
                    lyrInfrastructureClip, "TechnicalInfrastructure_Clip"
                )
                self.generalFunctions.writeVectorLayer(lyrRoadsClip, "Roads_Clip")
                self.generalFunctions.writeVectorLayer(
                    lyrBuildingsClip, "Buildings_Clip"
                )

        if self.generalFunctions.filePresent("HazardArea"):
            self.generalFunctions.addLayer("HazardArea", "LayerStyle_HazardArea")
            self.generalFunctions.addLayer("TechnicalInfrastructure_Clip", "LayerStyle_TechnicalInfrastructure")
            self.generalFunctions.addLayer("Roads_Clip", "LayerStyle_Roads")
            self.generalFunctions.addLayer("Buildings_Clip", "LayerStyle_Buildings")
            self.generalFunctions.addLayer("RiverineFlood_Clip", "LayerStyle_FloodRisk")
            self.generalFunctions.addLayer("PluvialFlood_Clip", "LayerStyle_FloodRisk")

        widget = iface.messageBar().createMessage("Step 5", "Calculating done!")
        iface.messageBar().pushWidget(widget, Qgis.Success)

    def runStep6(self):
        """Step 6: Change Type & Construction of already existing Buildings."""

        text = (
            "To change building type and type of construction of an existing "
            "building on the map, please first choose the new building type "
            "and type of construction in the drop down menus and press OK. "
            "Then you can choose the targeted buildings for the new values "
            "by freehand drawing on the map. \n\nIMPORTANT: Make sure you have selected (highlighted) the layer "
            "tempbuilding in the Layers Window. \n\nTo repeat this step for other buildings, just click again on button 6."
        )

        dlgBuildings = BuildingsDialog(text)
        dlgErrorMessage = ErrorMessageDialog()
        self.generalFunctions = GeneralFunctions(self.iface)

        try:
            self.step6 = Step6(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()
            return

        result = dlgBuildings.exec_()

        if result == QDialog.Accepted:

            type = dlgBuildings.type()
            construction = dlgBuildings.construction()

            self.step6.changeBuilding(type, construction)

    def runStep7(self):
        """Step 7: Add Building incl. Type & Construction."""

        text = (
            "To add new building to the map, please first choose the new building type "
            "and type of construction in the drop down menus and press OK. "
            "Then draw the building on the map using left click for edges and right click for finishing \n\n"
            "IMPORTANT:  Make sure you have selected (highlighted) the layer "
            "Builddings_Clip in the Layers Window. \n\nTo repeat this step for other buildings, just click again on \nbutton 7."
        )

        dlgBuildings = BuildingsDialog(text)
        dlgErrorMessage = ErrorMessageDialog()

        try:
            self.step7 = Step7(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()
            return

        result = dlgBuildings.exec_()

        if result == QDialog.Accepted:

            type = dlgBuildings.type()
            construction = dlgBuildings.construction()

            self.step7.addBuilding(type, construction)

    def runStep8(self):
        """Step 8: Add Technical Infrastructure."""

        text = (
            "To add new technical infrastructure to the map, please first choose the new building type "
            "and type of construction in the drop down menus and press OK. "
            "Then draw the technical infrastructure on the map using left click for edges and right click for finishing \n\n"
            "IMPORTANT: Make sure you have selected (highlighted) the layer "
            "technical infrastructure in the Layers Window. \n\nTo repeat this step for other technical infrastructures, just click again on button 8."
        )

        dlgInfrastructure = InfrastructureDialog(text)
        dlgInfrastructure.cb_Type.addItems(
            [
                "PowerStation",
                "PowerGrid",
                "SanitationNetworks",
                "WaterTanks",
                "DrainageSystem",
                "CommunicationInfrastructure",
            ]
        )

        self.step8 = Step8(self.iface)

        result = dlgInfrastructure.exec_()

        if result == QDialog.Accepted:

            type = dlgInfrastructure.type()

            self.step8.addInfrastrucutre(type)

    def runStep9(self):
        """Step 9: Add Transport Infrastructure."""

        text = (
            "To add new transport infrastructure to the map, please first choose the new building type "
            "and type of construction in the drop down menus and press OK. "
            "Then draw the technical infrastructure on the map using left click for edges and right click for finishing \n\n"
            "IMPORTANT: Make sure you have selected (highlighted) the layer "
            "technical infrastructure in the Layers Window. \n\nTo repeat this step for other technical infrastructures, just click again on button 8."
        )

        dlgInfrastructure = InfrastructureDialog(text)
        dlgInfrastructure.cb_Type.addItems(["road", "bridge"])
        dlgErrorMessage = ErrorMessageDialog()

        try:
            self.step9 = Step9(self.iface)

        except Exception as e:

            if "is not available" in str(e):
                dlgErrorMessage.setText(
                    "Error: " + str(e),
                    "You may not have performed the previous steps that create this layer.",
                )
            else:
                dlgErrorMessage.setText("Error: " + str(e), "An unknown error occured.")

            dlgErrorMessage.exec_()
            # self.iface.messageBar().clearWidgets()
            return

        result = dlgInfrastructure.exec_()

        if result == QDialog.Accepted:

            type = dlgInfrastructure.type()

            self.step9.addInfrastructure(type)

    def runStep10(self):
        """Step 10: Calculate Hazard."""

        self.generalFunctions = GeneralFunctions(self.iface)
        self.step10 = Step10(self.iface)
        self.absPath = QgsProject.instance().absolutePath()
        self.loadingBar = LoadingBar("Calculating...")

        self.generalFunctions.removeLayer("Roads_RiverineFlood_Risk")
        self.generalFunctions.removeLayer("Roads_PluvialFlood_Risk")
        self.generalFunctions.removeLayer("Buildings_RiverineFlood_Risk")
        self.generalFunctions.removeLayer("Buildings_PluvialFlood_Risk")
        self.generalFunctions.removeLayer("TechnicalInfrastructure_RiverineFlood_Risk")
        self.generalFunctions.removeLayer("TechnicalInfrastructure_PluvialFlood_Risk")

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        if self.generalFunctions.filePresent("Roads_RiverineFlood_Risk"):
            dlgMessage.setText(
                "In this step, calculations are carried out on the risk intensity of buildings, "
                "transport infrastructure and technical infrastructure.\n\n"
                "You have already calculated risks. Do you want to calculate them again?"
            )

        else:
            dlgMessage.setText(
                "In this step, calculations are carried out on the risk intensity of buildings, "
                "transport infrastructure and technical infrastructure."
            )

        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            def calculate():

                try:
                    self.generalFunctions.removeShpFile("Roads_Riverine_Clip")
                    self.generalFunctions.removeShpFile("Roads_Pluvial_Clip")
                    self.generalFunctions.removeShpFile("Buildings_Riverine_Clip")
                    self.generalFunctions.removeShpFile("Buildings_Pluvial_Clip")
                    self.generalFunctions.removeShpFile("Infrastructure_Riverine_Clip")
                    self.generalFunctions.removeShpFile("Infrastructure_Pluvial_Clip")

                except PermissionError as e:
                    dlgErrorMessage.setText(
                        "Error: " + str(e) + ".",
                        "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                    )
                    dlgErrorMessage.exec_()
                    return

                # join attribute by location
                self.step10.spatialJoin(
                    "Roads_Clip", "RiverineFlood_Clip", "Roads_Riverine_Clip"
                )
                self.step10.spatialJoin(
                    "Roads_Clip", "PluvialFlood_Clip", "Roads_Pluvial_Clip"
                )

                self.step10.spatialJoin(
                    "Buildings_Clip", "RiverineFlood_Clip", "Buildings_Riverine_Clip"
                )
                self.step10.spatialJoin(
                    "Buildings_Clip", "PluvialFlood_Clip", "Buildings_Pluvial_Clip"
                )

                self.step10.spatialJoin(
                    "TechnicalInfrastructure_Clip",
                    "RiverineFlood_Clip",
                    "Infrastructure_Riverine_Clip",
                )
                self.step10.spatialJoin(
                    "TechnicalInfrastructure_Clip",
                    "PluvialFlood_Clip",
                    "Infrastructure_Pluvial_Clip",
                )

                # clip camp area
                lyrRoadsRiverine_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Roads_Riverine_Clip.shp"
                )
                lyrRoadsPluvial_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Roads_Pluvial_Clip.shp"
                )

                lyrBuildingsRiverine_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Buildings_Riverine_Clip.shp"
                )
                lyrBuildingsPluvial_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Buildings_Pluvial_Clip.shp"
                )

                lyrInfrastructureRiverine_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Infrastructure_Riverine_Clip.shp"
                )
                lyrInfrastructurePluvial_Clip = self.generalFunctions.clipCampArea(
                    self.absPath + "/Infrastructure_Pluvial_Clip.shp"
                )

                # Add fields
                self.step10.addFields(lyrRoadsRiverine_Clip)
                self.step10.addFields(lyrRoadsPluvial_Clip)
                self.step10.addFields(lyrBuildingsRiverine_Clip)
                self.step10.addFields(lyrBuildingsPluvial_Clip)
                self.step10.addFields(lyrInfrastructureRiverine_Clip)
                self.step10.addFields(lyrInfrastructurePluvial_Clip)

                # set field values
                self.step10.setValuesRoadsRiv(lyrRoadsRiverine_Clip)
                self.step10.setValuesRoadsPluv(lyrRoadsPluvial_Clip)
                self.step10.setValuesBuildingsRiv(lyrBuildingsRiverine_Clip)
                self.step10.setValuesBuildingsPluv(lyrBuildingsPluvial_Clip)
                self.step10.setValuesInfrastructureRiv(lyrInfrastructureRiverine_Clip)
                self.step10.setValuesInfrastructurePluv(lyrInfrastructurePluvial_Clip)

                if self.generalFunctions.filePresent("Roads_RiverineFlood_Risk"):

                    self.generalFunctions.writeTempFile(
                        lyrRoadsRiverine_Clip,
                        "Roads_RiverineFlood_Risk_temp",
                        "Roads_RiverineFlood_Risk",
                    )
                    self.generalFunctions.writeTempFile(
                        lyrRoadsPluvial_Clip,
                        "Roads_PluvialFlood_Risk_temp",
                        "Roads_PluvialFlood_Risk",
                    )
                    self.generalFunctions.writeTempFile(
                        lyrBuildingsRiverine_Clip,
                        "Buildings_RiverineFlood_Risk_temp",
                        "Buildings_RiverineFlood_Risk",
                    )
                    self.generalFunctions.writeTempFile(
                        lyrBuildingsPluvial_Clip,
                        "Buildings_PluvialFlood_Risk_temp",
                        "Buildings_PluvialFlood_Risk",
                    )
                    self.generalFunctions.writeTempFile(
                        lyrInfrastructureRiverine_Clip,
                        "TechnicalInfrastructure_RiverineFlood_Risk_temp",
                        "TechnicalInfrastructure_RiverineFlood_Risk",
                    )
                    self.generalFunctions.writeTempFile(
                        lyrInfrastructurePluvial_Clip,
                        "TechnicalInfrastructure_PluvialFlood_Risk_temp",
                        "TechnicalInfrastructure_PluvialFlood_Risk",
                    )

                else:
                    self.generalFunctions.writeVectorLayer(
                        lyrRoadsRiverine_Clip, "Roads_RiverineFlood_Risk"
                    )
                    self.generalFunctions.writeVectorLayer(
                        lyrRoadsPluvial_Clip, "Roads_PluvialFlood_Risk"
                    )
                    self.generalFunctions.writeVectorLayer(
                        lyrBuildingsRiverine_Clip, "Buildings_RiverineFlood_Risk"
                    )
                    self.generalFunctions.writeVectorLayer(
                        lyrBuildingsPluvial_Clip, "Buildings_PluvialFlood_Risk"
                    )
                    self.generalFunctions.writeVectorLayer(
                        lyrInfrastructureRiverine_Clip,
                        "TechnicalInfrastructure_RiverineFlood_Risk",
                    )
                    self.generalFunctions.writeVectorLayer(
                        lyrInfrastructurePluvial_Clip,
                        "TechnicalInfrastructure_PluvialFlood_Risk",
                    )

            self.loadingBar.upload_file_operation(uploadFunction=calculate)

        ###

        # do not display empty layers and also do not display layers of flood that are emtpy
        # sort so that layer with a lot no data are below other layers

        layers = [
            {"name": "Roads_RiverineFlood_Risk", "style": "LayerStyle_Step10_Line"},
            {"name": "Roads_PluvialFlood_Risk", "style": "LayerStyle_Step10_Line"},
            {"name": "Buildings_RiverineFlood_Risk", "style": "LayerStyle_Step10_Polygon"},
            {"name": "Buildings_PluvialFlood_Risk", "style": "LayerStyle_Step10_Polygon"},
            {"name": "TechnicalInfrastructure_RiverineFlood_Risk", "style": "LayerStyle_Step10_Polygon"},
            {"name": "TechnicalInfrastructure_PluvialFlood_Risk", "style": "LayerStyle_Step10_Polygon"},
        ]

        layers = [layer for layer in layers if not self.generalFunctions.isLayerEmpty(layer["name"])]

        for layer in layers:
            if not self.generalFunctions.isLayerEmpty(layer["name"]):
                layer["layer"] = self.generalFunctions.getVectorLayer(self.absPath + "/" + layer["name"] + ".shp", layer["name"])

        # Function to calculate the sum of "SumVul" field
        def calculate_sum_vul(layer):
            sum_vul = 0
            # Assuming each layer is a QGIS vector layer and "SumVul" is a field in that layer
            for feature in layer["layer"].getFeatures():
                sum_vul += feature['SumVul']  # Sum values from "SumVul" field
            return sum_vul
 
        for layer in layers:
            layer["sumVul"] = calculate_sum_vul(layer)

        # Sort the valid layers by "SumVul" in descending order (highest first)
        layers.sort(key=lambda x: x["sumVul"])

        # Add layers to QGIS with the one with the highest "SumVul" last
        for layer in layers:
            self.generalFunctions.addLayer(layer["name"], layer["style"])  # Add layer to QGIS

        ###


        # don't display pluvial flood if empty
        # if not self.generalFunctions.isLayerEmpty("PluvialFlood_Clip"):

        #     if self.generalFunctions.filePresent("Roads_PluvialFlood_Risk"):
        #         self.generalFunctions.addLayer(
        #             "Roads_PluvialFlood_Risk", "LayerStyle_Step10_Line"
        #         )
        #         self.generalFunctions.addLayer(
        #             "Buildings_PluvialFlood_Risk", "LayerStyle_Step10_Polygon"
        #         )
        #         self.generalFunctions.addLayer(
        #             "TechnicalInfrastructure_PluvialFlood_Risk", "LayerStyle_Step10_Polygon"
        #         )
        # if self.generalFunctions.filePresent("Roads_RiverineFlood_Risk"):
        #     self.generalFunctions.addLayer(
        #         "Roads_RiverineFlood_Risk", "LayerStyle_Step10_Line"
        #     )
        #     self.generalFunctions.addLayer(
        #         "Buildings_RiverineFlood_Risk", "LayerStyle_Step10_Polygon"
        #     )
        #     self.generalFunctions.addLayer(
        #         "TechnicalInfrastructure_RiverineFlood_Risk", "LayerStyle_Step10_Polygon"
        #     )

    def runStep11(self):
        """Step 11: Adjust risk."""

        message = (
            "To adjust the risk level manually, first choose the layer (type of "
            "asset and flood) from the drop down menu. Then select the "
            "new risk level value (1-5). After pressing OK, you can select the "
            "area to be adjusted using left click for edges and right click for "
            "finishing. \n\nIMPORTANT: Make sure the temp layer is selected "
            "(highlighted) in the Layers Window. \n\nTo change the risk level of several zones, repeat this step (button 11). \n"
        )

        dlgRiskAdjustment = RiskAdjustmentDialog(message)

        self.step11 = Step11(self.iface)

        result = dlgRiskAdjustment.exec_()

        if result == QDialog.Accepted:

            layer = dlgRiskAdjustment.getLayer()
            risk = dlgRiskAdjustment.getRisk()

            self.step11.changeRisk(layer, risk)

    # def runStep12(self):
    #     """Step 12: Export Risk Map"""

    #     self.generalFunctions = GeneralFunctions(self.iface)
    #     self.step12 = Step12(self.iface)
    #     self.absPath = QgsProject.instance().absolutePath()

    #     dlgErrorMessage = ErrorMessageDialog()
    #     dlgMessage = MessageDialog()

    #     if self.generalFunctions.filePresent(
    #         "Output_RiskMap_Riverine", ".pdf"
    #     ):
    #         dlgMessage.setText(
    #             "In this step, the Risk Maps will be exported as PDF.\n\n"
    #             "You have already exported risk maps. Do you want to export them again? "
    #             "IMPORTANT: The existing maps will be overwritten. If you want to keep them, you should copy them to another folder."
    #         )

    #     else:
    #         dlgMessage.setText("In this step, the Risk Maps will be exported as PDF.")

    #     result = dlgMessage.exec_()

    #     if result == QDialog.Accepted:

    #         try:
    #             self.generalFunctions.removeShpFile("Output_RiskMap_Riverine")
    #             self.generalFunctions.removeShpFile("Output_RiskMap_Pluvial")

    #         except PermissionError as e:
    #             dlgErrorMessage.setText(
    #                 "Error: " + str(e) + ".",
    #                 "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
    #             )
    #             dlgErrorMessage.exec_()
    #             return

    #         self.step12.setupMap(
    #             [
    #                 "Buildings_RiverineFlood_Risk",
    #                 "Roads_RiverineFlood_Risk",
    #                 "TechnicalInfrastructure_RiverineFlood_Risk",
    #             ]
    #         )

    #         ##
    #         # layoutManager = QgsProject.instance().layoutManager()
    #         # layoutName = "LayoutRiskMapRiverine"

    #         # existingLayout = None
    #         # for layout in layoutManager.printLayouts():
    #         #     if layout.name() == layoutName:
    #         #         existing_layout = layout
    #         #         break

    #         # if existing_layout:
    #         #     # Open the layout in the Layout Editor
    #         #     dialog = QgsLayoutDesignerDialog(existingLayout)
    #         #     dialog.show()
    #         ##

    #         #self.step12.openLayout(self.absPath + "/LayoutRiskMapTest.qpt","LayoutRiskMapRiverine")

    #         self.step12.exportLayoutAsPDF(
    #             "LayoutRiskMapRiverine",
    #             "Risk Map - Riverine Flood",
    #             "Output_RiskMap_Riverine",
    #         )

    #         if not self.generalFunctions.isLayerEmpty("PluvialFlood_Clip"):
    #             self.step12.setupMap(
    #                 [
    #                     "Buildings_PluvialFlood_Risk",
    #                     "Roads_PluvialFlood_Risk",
    #                     "TechnicalInfrastructure_PluvialFlood_Risk",
    #                 ]
    #             )
    #             self.step12.exportLayoutAsPDF(
    #                 "LayoutRiskMapPluvial",
    #                 "Risk Map - Pluvial Flood",
    #                 "Output_RiskMap_Pluvial",
    #             )

    #         widget = iface.messageBar().createMessage("Step 12", "Exporting done!")
    #         iface.messageBar().pushWidget(widget, Qgis.Success)

    def runStep12Riverine(self):
        """Step 12: Export Risk Map Riverine"""

        self.generalFunctions = GeneralFunctions(self.iface)
        self.step12 = Step12(self.iface)
        self.absPath = QgsProject.instance().absolutePath()

        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        #dlgMessageYesNo = MessageDialogYesNo()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        if self.generalFunctions.isLayerEmpty("RiverineFlood_Clip"):

            dlgMessage.setText(
                "The Riverine Flood risk map is empty and will not be exported."
            )

            dlgMessage.exec_()

        else:

            if self.generalFunctions.filePresent(
                "Output_RiskMap_Riverine", ".pdf"
            ):
                dlgMessage.setText(
                    "In this step, the Riverine Risk Map will be exported as PDF.\n\n"
                    "You have already exported this risk map. Do you want to export ist again? "
                    "IMPORTANT: The existing mapswill be overwritten. If you want to keep it, you should copy it to another folder."
                )

            else:
                dlgMessage.setText("In this step, the Riverine Risk Map will be exported as PDF.")

            result = dlgMessage.exec_()

            if result == QDialog.Accepted:

                try:
                    self.generalFunctions.removeShpFile("Output_RiskMap_Riverine")

                except PermissionError as e:
                    dlgErrorMessage.setText(
                        "Error: " + str(e) + ".",
                        "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                    )
                    dlgErrorMessage.exec_()
                    return
                

                dlgChoosePrint.setText(
                    "Do you want the Risk Map to be exported automatically or manually?"
                )

                result = dlgChoosePrint.exec_()

                if result == QDialog.Accepted:

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step12.setupMap(
                            [
                                "Buildings_RiverineFlood_Risk",
                                "Roads_RiverineFlood_Risk",
                                "TechnicalInfrastructure_RiverineFlood_Risk",
                            ]
                        )

                        # self.step12.exportLayoutAsPDF(
                        # "LayoutRiskMapRiverine",
                        # "Risk Map - Riverine Flood",
                        # "Output_RiskMap_Riverine",
                        # )

                        self.step12.exportLayoutAsPDFusingTemplate(self.absPath + "/LayoutRiskMapRiverine.qpt", "Output_RiskMap_Riverine")

                        widget = iface.messageBar().createMessage("Step 12", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        self.step12.openLayout(self.absPath + "/LayoutRiskMapRiverine.qpt")
                

            ##
            # layoutManager = QgsProject.instance().layoutManager()
            # layoutName = "LayoutRiskMapRiverine"

            # existingLayout = None
            # for layout in layoutManager.printLayouts():
            #     if layout.name() == layoutName:
            #         existing_layout = layout
            #         break

            # if existing_layout:
            #     # Open the layout in the Layout Editor
            #     dialog = QgsLayoutDesignerDialog(existingLayout)
            #     dialog.show()
            ##

                
    def runStep12Pluvial(self):
            """Step 12: Export Risk Map Pluvial"""

            self.generalFunctions = GeneralFunctions(self.iface)
            self.step12 = Step12(self.iface)
            self.absPath = QgsProject.instance().absolutePath()

            dlgErrorMessage = ErrorMessageDialog()
            dlgMessage = MessageDialog()
            dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

            if self.generalFunctions.isLayerEmpty("PluvialFlood_Clip"):

                dlgMessage.setText(
                    "The Pluvial Flood risk map is empty and will not be exported."
                )
                
                dlgMessage.exec_()

            else:

                if self.generalFunctions.filePresent(
                    "Output_RiskMap_Pluvial", ".pdf"
                ):
                    dlgMessage.setText(
                        "In this step, the Pluvial Risk Map will be exported as PDF.\n\n"
                        "You have already exported this risk map. Do you want to export it again? "
                        "IMPORTANT: The existing map will be overwritten. If you want to keep it, you should copy it to another folder."
                    )

                else:
                    dlgMessage.setText("In this step, the Pluvial Risk Map will be exported as PDF.")

                result = dlgMessage.exec_()

                if result == QDialog.Accepted:

                    try:
                        self.generalFunctions.removeShpFile("Output_RiskMap_Pluvial")

                    except PermissionError as e:
                        dlgErrorMessage.setText(
                            "Error: " + str(e) + ".",
                            "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                        )
                        dlgErrorMessage.exec_()
                        return
                    

                    dlgChoosePrint.setText(
                    "Do you want the Risk Map to be exported automatically or manually?"
                    )

                    result = dlgChoosePrint.exec_()

                    if result == QDialog.Accepted:

                        if dlgChoosePrint.chosenOption() == "automatically":

                            self.step12.setupMap(
                                [
                                    "Buildings_PluvialFlood_Risk",
                                    "Roads_PluvialFlood_Risk",
                                    "TechnicalInfrastructure_PluvialFlood_Risk",
                                ]
                            )

                            # self.step12.exportLayoutAsPDF(
                            #     "LayoutRiskMapPluvial",
                            #     "Risk Map - Pluvial Flood",
                            #     "Output_RiskMap_Pluvial",
                            # )

                            self.step12.exportLayoutAsPDFusingTemplate(self.absPath + "/LayoutRiskMapPluvial.qpt", "Output_RiskMap_Pluvial")

                            widget = iface.messageBar().createMessage("Step 12", "Exporting done!")
                            iface.messageBar().pushWidget(widget, Qgis.Success)

                        elif dlgChoosePrint.chosenOption() == "manually":

                            self.step12.openLayout(self.absPath + "/LayoutRiskMapPluvial.qpt")
                

    def runStep13(self):
        """Step 13: Choose Measurements"""

        dlgCheckMeasures = CheckMeasuresDialog()
        dlgErrorMessage = ErrorMessageDialog()
        self.step13 = Step13(self.iface)
        self.generalFunctions = GeneralFunctions(self.iface)

        result = dlgCheckMeasures.exec_()

        if result == QDialog.Accepted:

            lyrMeasures = QgsProject.instance().mapLayersByName("Measures")[0]

            dfMeasures = self.step13.getMeasuresDf(lyrMeasures)

            dfChecks = dlgCheckMeasures.getCheckboxStates()

            self.checksText = dlgCheckMeasures.getCheckboxText()

            measuresTOI = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "TOI")
            measuresSOI = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "SOI")
            measuresST = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "ST")
            measuresTime = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "Time")
            measuresDuration = self.step13.getCheckedMeasures(
                dfMeasures, dfChecks, "Duration"
            )
            measuresIC = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "IC")
            measuresMC = self.step13.getCheckedMeasures(dfMeasures, dfChecks, "MC")

            pluvialChecked = dfChecks.loc[:, "TNH_Pluvial"].item()
            riverineChecked = dfChecks.loc[:, "TNH_Coastal_Riverine"].item()
            buildingsChecked = dfChecks.loc[:, "TVA_Buildings"].item()
            transportChecked = dfChecks.loc[:, "TVA_Transport"].item()
            technicalChecked = dfChecks.loc[:, "TVA_Technical_Infrastructure"].item()
            landcoverChecked = dfChecks.loc[:, "TVA_Land_Cover"].item()

            # Find the common measures across all sets
            measures = reduce(
                np.intersect1d,
                [
                    measuresTOI,
                    measuresSOI,
                    measuresST,
                    measuresTime,
                    measuresDuration,
                    measuresIC,
                    measuresMC,
                ],
            )

            measuresPluvial = self.step13.getMeasuresApp(dfMeasures, "TNH_Pluvial")
            measuresRiverine = self.step13.getMeasuresApp(
                dfMeasures, "TNH_Coastal_Riverine"
            )
            measuresBuildings = self.step13.getMeasuresApp(dfMeasures, "TVA_Buildings")
            measuresTransport = self.step13.getMeasuresApp(dfMeasures, "TVA_Transport")
            measuresTechnical = self.step13.getMeasuresApp(
                dfMeasures, "TVA_Technical_Infrastructure"
            )
            measuresLand = self.step13.getMeasuresApp(dfMeasures, "TVA_Land_Cover")

            if pluvialChecked:

                if buildingsChecked:
                    measuresPluvialBuilding = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresPluvial,
                            measuresBuildings,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures,
                        measuresPluvialBuilding,
                        "Measures_Pluvial_Building",
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Pluvial_Building")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Pluvial_Building as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Pluvial_Building")
                        dlgErrorMessage.exec_()

                if transportChecked:
                    measuresPluvialTransport = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresPluvial,
                            measuresTransport,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures, measuresPluvialTransport, "Measures_Pluvial_Road"
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Pluvial_Road")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Pluvial_Road as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Pluvial_Road")
                        dlgErrorMessage.exec_()

                if technicalChecked:
                    measuresPluvialTechnical = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresPluvial,
                            measuresTechnical,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures,
                        measuresPluvialTechnical,
                        "Measures_Pluvial_TechnicalInfrastructure",
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Pluvial_TechnicalInfrastructure")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Pluvial_TechnicalInfrastructure as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer(
                            "Measures_Pluvial_TechnicalInfrastructure"
                        )
                        dlgErrorMessage.exec_()
                if landcoverChecked:
                    measuresPluvialLand = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresPluvial,
                            measuresLand,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures, measuresPluvialLand, "Measures_Pluvial_LandCover"
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Pluvial_LandCover")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Pluvial_LandCover as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Pluvial_LandCover")
                        dlgErrorMessage.exec_()

            if riverineChecked:
                if buildingsChecked:
                    measuresRiverineBuilding = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresRiverine,
                            measuresBuildings,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures,
                        measuresRiverineBuilding,
                        "Measures_Riverine_Building",
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Riverine_Building")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Riverine_Building as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Riverine_Building")
                        dlgErrorMessage.exec_()

                if transportChecked:
                    measuresRiverineTransport = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresRiverine,
                            measuresTransport,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures, measuresRiverineTransport, "Measures_Riverine_Road"
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Riverine_Road")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Riverine_Road as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Riverine_Road")
                        dlgErrorMessage.exec_()

                if technicalChecked:
                    measuresRiverineTechnical = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresRiverine,
                            measuresTechnical,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures,
                        measuresRiverineTechnical,
                        "Measures_Riverine_TechnicalInfrastructure",
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Riverine_TechnicalInfrastructure")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Riverine_TechnicalInfrastructure as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer(
                            "Measures_Riverine_TechnicalInfrastructure"
                        )
                        dlgErrorMessage.exec_()

                if landcoverChecked:
                    measuresRiverineLand = reduce(
                        np.intersect1d,
                        [
                            measures,
                            measuresRiverine,
                            measuresLand,
                        ],
                    )
                    self.step13.createLayer(
                        lyrMeasures, measuresRiverineLand, "Measures_Riverine_LandCover"
                    )
                    if (
                        QgsProject.instance()
                        .mapLayersByName("Measures_Riverine_LandCover")[0]
                        .featureCount()
                        < 1
                    ):
                        dlgErrorMessage.setText(
                            "Could not create layer Measures_Riverine_LandCover as it is an empty layer.",
                            "Unable to find measures that match the selected parameters. Please review and adjust your parameters.",
                        )
                        self.generalFunctions.removeLayer("Measures_Riverine_LandCover")
                        dlgErrorMessage.exec_()

    def runStep14RiverineRoad(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_Road_Riverine.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Roads affected by Riverine. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Roads affected by Riverine Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Riverine_Road"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("Roads_RiverineFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintRoadRiverine",
                            "Measures Roads - Riverine Flood",
                            "Measures_Riverine_Road",
                            "Output_Road_Riverine",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures Roads - Riverine Flood",
                            "Measures_Riverine_Road",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Riverine_Road not available.",
                        "Output_Road_Riverine cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()

    def runStep14RiverineBuilding(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_Building_Riverine.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Buildings affected by Riverine. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Buildings affected by Riverine Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Riverine_Building"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("Buildings_RiverineFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintBuildingRiverine",
                            "Measures Building - Riverine Flood",
                            "Measures_Riverine_Building",
                            "Output_Building_Riverine",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures Building - Riverine Flood",
                            "Measures_Riverine_Building",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Riverine_Building not available.",
                        "Output_Building_Riverine cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()
        

    def runStep14RiverineInfrastructure(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_TechnicalInfrastrucutre_Riverine.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Technical Infrastructure affected by Riverine. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Technical Infrastructure affected by Riverine Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Riverine_TechnicalInfrastructure"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("TechnicalInfrastructure_RiverineFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintTechnicalInfrastructureRiverine",
                            "Measures Technical Infrastructure - Riverine Flood",
                            "Measures_Riverine_TechnicalInfrastructure",
                            "Output_TechnicalInfrastructure_Riverine",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures Technical Infrastructure - Riverine Flood",
                            "Measures_Riverine_TechnicalInfrastructure",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Riverine_TechnicalInfrastructure not available.",
                        "Output_TechnicalInfrastructure_Riverine cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()

    def runStep14PluvialRoad(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_Road_Pluvial.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Roads affected by Pluvial Flood. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Roads affected by Pluvial Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Pluvial_Road"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("Roads_PluvialFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintRoadPluvial",
                            "Measures Roads - Pluvial Flood",
                            "Measures_Pluvial_Road",
                            "Output_Road_Pluvial",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures Roads - Pluvial Flood",
                            "Measures_Pluvial_Road",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Pluvial_Road not available.",
                        "Output_Road_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()

    def runStep14PluvialBuilding(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_Building_Pluvial.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Buildings affected by Pluvial Flood. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Buildings affected by Pluvial Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Pluvial_Building"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("Buildings_PluvialFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintBuildingPluvial",
                            "Measures Building - Pluvial Flood",
                            "Measures_Pluvial_Building",
                            "Output_Building_Pluvial",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures Building - Pluvial Flood",
                            "Measures_Pluvial_Building",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Pluvial_Building not available.",
                        "Output_Building_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()

    def runStep14PluvialInfrastructure(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()
        dlgChoosePrint = ChooseOptionDialog(["automatically", "manually"])

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"
        filepath = folderpath + "Output_TechnicalInfrastructure_Pluvial.pdf"

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        if os.path.exists(filepath):
            dlgMessage.setText(
                "You have already exported measures for Technical Infrustructure affected by Pluvial Flood. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find a PDF with measures for Technical Infrustructure affected by Pluvial Flood."
            )
        
        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)

                checksText = self.checksText

            except PermissionError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                )
                dlgErrorMessage.exec_()
                return
            
            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            dlgChoosePrint.setText(
            "Do you want the Measures to be exported automatically or manually?"
            )

            result = dlgChoosePrint.exec_()

            if result == QDialog.Accepted:

                if QgsProject.instance().mapLayersByName("Measures_Pluvial_TechnicalInfrastructure"):

                    if dlgChoosePrint.chosenOption() == "automatically":

                        self.step14.setupMap("TechnicalInfrastructure_PluvialFlood_Risk")

                        self.step14.exportLayoutAsPDF(
                            "PrintTechnicalInfrastructurePluvial",
                            "Measures Technical Infrastructure - Pluvial Flood",
                            "Measures_Pluvial_TechnicalInfrastructure",
                            "Output_TechnicalInfrastructure_Pluvial",
                            checksText
                        )

                        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
                        iface.messageBar().pushWidget(widget, Qgis.Success)

                    elif dlgChoosePrint.chosenOption() == "manually":

                        layout = self.step14.createLayout(
                            "Measures_Pluvial_TechnicalInfrastructure",
                            "Output_TechnicalInfrastructure_Pluvial",
                            checksText)

                        self.step14.openLayout(layout)
                
                else:
                    dlgErrorMessage.setText(
                        "Layer Measures_Pluvial_TechnicalInfrastructure not available.",
                        "Output_TechnicalInfrastructure_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
                    )
                    dlgErrorMessage.exec_()

    def runStep14RiskStats(self):
        """Step 12: Export Risk Map Pluvial"""

        self.step14 = Step14(self.iface)
        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"

        lyr_risksBuildingsRiverine = QgsVectorLayer(
                (self.absPath + "/Buildings_RiverineFlood_Risk.shp"),
                "Buildings_RiverineFlood_RiskData",
                "ogr",
            )
        lyr_risksBuildingsPluvial = QgsVectorLayer(
            (self.absPath + "/Buildings_PluvialFlood_Risk.shp"),
            "Buildings_PluvialFlood_RiskData",
            "ogr",
        )
        lyr_risksTechRiverine = QgsVectorLayer(
            (self.absPath + "/TechnicalInfrastructure_RiverineFlood_Risk.shp"),
            "TechnicalInfrastructure_RiverineFlood_RiskData",
            "ogr",
        )
        lyr_risksTechPluvial = QgsVectorLayer(
            (self.absPath + "/TechnicalInfrastructure_PluvialFlood_Risk.shp"),
            "TechnicalInfrastructure_PluvialFlood_RiskData",
            "ogr",
        )
        lyr_risksRoadsRiverine = QgsVectorLayer(
            (self.absPath + "/Roads_RiverineFlood_Risk.shp"),
            "Roads_RiverineFlood_RiskData",
            "ogr",
        )
        lyr_risksRoadsPluvial = QgsVectorLayer(
            (self.absPath + "/Roads_PluvialFlood_Risk.shp"),
            "Roads_PluvialFlood_RiskData",
            "ogr",
        )

        dfBuildRiv = self.step14.getDf(lyr_risksBuildingsRiverine)
        dfBuildRiv = self.step14.editAttributeTable(
            dfBuildRiv, "Buildings", "Riverine"
        )

        dfBuildPluv = self.step14.getDf(lyr_risksBuildingsPluvial)
        dfBuildPluv = self.step14.editAttributeTable(
            dfBuildPluv, "Buildings", "Pluvial"
        )

        dfTechRiv = self.step14.getDf(lyr_risksTechRiverine)
        dfTechRiv = self.step14.editAttributeTable(
            dfTechRiv, "TechnicalInfrastructure", "Riverine"
        )

        dfTechPluv = self.step14.getDf(lyr_risksTechPluvial)
        dfTechPluv = self.step14.editAttributeTable(
            dfTechPluv, "TechnicalInfrastructure", "Pluvial"
        )

        dfRoadsRiv = self.step14.getDf(lyr_risksRoadsRiverine)
        dfRoadsRiv = self.step14.editAttributeTable(dfRoadsRiv, "Roads", "Riverine")

        dfRoadsPluv = self.step14.getDf(lyr_risksRoadsPluvial)
        dfRoadsPluv = self.step14.editAttributeTable(
            dfRoadsPluv, "Roads", "Pluvial"
        )

        dfRisks = pd.DataFrame(
            columns=["Asset_Type", "Asset", "Flood_Type", "Risk", "Count"]
        )

        dfRisks = self.step14.createRiskDataTable(
            dfBuildRiv, dfRisks, "Buildings", "Riverine"
        )
        dfRisks = self.step14.createRiskDataTable(
            dfBuildPluv, dfRisks, "Buildings", "Pluvial"
        )
        dfRisks = self.step14.createRiskDataTable(
            dfTechRiv, dfRisks, "TechnicalInfrastructure", "Riverine"
        )
        dfRisks = self.step14.createRiskDataTable(
            dfTechPluv, dfRisks, "TechnicalInfrastructure", "Pluvial"
        )
        dfRisks = self.step14.createRiskDataTable(
            dfRoadsRiv, dfRisks, "Roads", "Riverine"
        )
        dfRisks = self.step14.createRiskDataTable(
            dfRoadsPluv, dfRisks, "Roads", "Pluvial"
        )

        # Export risk statistics as excel
        filepath = folderpath + "/riskStats.xlsx"
        dfRisks.to_excel(filepath, index=False) #index=False nötig?

        widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
        iface.messageBar().pushWidget(widget, Qgis.Success)
    
    def runStep14Old(self):
        """Step 14: Export Mitigation Actions"""

        self.step14 = Step14(self.iface)

        dlgMessage = MessageDialog()
        dlgErrorMessage = ErrorMessageDialog()
        dlgMessage = MessageDialog()

        self.absPath = QgsProject.instance().absolutePath()
        folderpath = self.absPath + "/Measures/"

        if os.path.exists(folderpath):
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find PDFs for all types of risks including "
                "the table with measures to look at in the catalogue.\n\n"
                "You have already exported measures. Do you want to export them again? "
                "IMPORTANT: The existing measures will be overwritten. If you want to keep them, you should copy them to another folder."
            )

        else:
            dlgMessage.setText(
                "After pressing OK a folder in your project-directory will be created named "
                "''Measures''. There you will find PDFs for all types of risks including "
                "the table with measures to look at in the catalogue."
            )

        result = dlgMessage.exec_()

        if result == QDialog.Accepted:

            if os.path.exists(folderpath):

                content = os.listdir(folderpath)

                if len(content) > 0:

                    try:

                        self.step14.removePdfFiles(folderpath)

                    except PermissionError as e:
                        dlgErrorMessage.setText(
                            "Error: " + str(e) + ".",
                            "The file cannot be overwritten. Please make sure that the file is not opened in another application and try again.",
                        )
                        dlgErrorMessage.exec_()
                        return

            else:
                os.makedirs(folderpath)

            try:

                checksText = self.checksText

            except AttributeError as e:
                dlgErrorMessage.setText(
                    "Error: " + str(e) + ".",
                    "Please complete the selection of measures in Step 13 first.",
                )
                dlgErrorMessage.exec_()
                return

            if QgsProject.instance().mapLayersByName("Measures_Riverine_Road"):

                self.step14.setupMap("Roads_RiverineFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintRoadRiverine",
                    "Measures Roads - Riverine Flood",
                    "Measures_Riverine_Road",
                    "Output_Road_Riverine",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Riverine_Road not available.",
            #         "Output_Road_Riverine cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName(
                "Measures_Riverine_TechnicalInfrastructure"
            ):
                self.step14.setupMap("TechnicalInfrastructure_RiverineFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintTechnicalInfrastructureRiverine",
                    "Measures Technical Infrastructure - Riverine Flood",
                    "Measures_Riverine_TechnicalInfrastructure",
                    "Output_TechnicalInfrastructure_Riverine",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Riverine_TechnicalInfrastructure not available.",
            #         "Output_TechnicalInfrastructure_Riverine cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Riverine_Building"):
                self.step14.setupMap("Buildings_RiverineFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintBuildingRiverine",
                    "Measures Building - Riverine Flood",
                    "Measures_Riverine_Building",
                    "Output_Building_Riverine",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Riverine_Building not available.",
            #         "Output_Building_Riverine cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Riverine_LandCover"):
                self.step14.setupMapEmpty()
                self.step14.exportLayoutAsPDF(
                    "PrintLandCoverRiverine",
                    "Measures Land Cover - Riverine Flood",
                    "Measures_Riverine_LandCover",
                    "Output_LandCover_Riverine",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Riverine_LandCover not available.",
            #         "Output_LandCover_Riverine cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Pluvial_Road"):
                self.step14.setupMap("Roads_PluvialFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintRoadPluvial",
                    "Measures Roads - Pluvial Flood",
                    "Measures_Pluvial_Road",
                    "Output_Road_Pluvial",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Pluvial_Road not available.",
            #         "Output_Road_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Pluvial_TechnicalInfrastructure"):
                self.step14.setupMap("TechnicalInfrastructure_PluvialFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintTechnicalInfrastructurePluvial",
                    "Measures Technical Infrastructure - Pluvial Flood",
                    "Measures_Pluvial_TechnicalInfrastructure",
                    "Output_TechnicalInfrastructure_Pluvial",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Pluvial_TechnicalInfrastructure not available.",
            #         "Output_TechnicalInfrastructure_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Pluvial_Building"):
                self.step14.setupMap("Buildings_PluvialFlood_Risk")
                self.step14.exportLayoutAsPDF(
                    "PrintBuildingPluvial",
                    "Measures Building - Pluvial Flood",
                    "Measures_Pluvial_Building",
                    "Output_Building_Pluvial",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Pluvial_Building not available.",
            #         "Output_Building_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            if QgsProject.instance().mapLayersByName("Measures_Pluvial_LandCover"):
                self.step14.setupMapEmpty()
                self.step14.exportLayoutAsPDF(
                    "PrintLandCoverPluvial",
                    "Measures Land Cover - Pluvial Flood",
                    "Measures_Pluvial_LandCover",
                    "Output_LandCover_Pluvial",
                    checksText
                )
            # else:
            #     dlgErrorMessage.setText(
            #         "Layer Measures_Pluvial_LandCover not available.",
            #         "Output_LandCover_Pluvial cannot be exported. Please review your selected parameters in Step 13.",
            #     )
            #     dlgErrorMessage.exec_()

            ### Export Risk Stats to Excel ###

            lyr_risksBuildingsRiverine = QgsVectorLayer(
                (self.absPath + "/Buildings_RiverineFlood_Risk.shp"),
                "Buildings_RiverineFlood_RiskData",
                "ogr",
            )
            lyr_risksBuildingsPluvial = QgsVectorLayer(
                (self.absPath + "/Buildings_PluvialFlood_Risk.shp"),
                "Buildings_PluvialFlood_RiskData",
                "ogr",
            )
            lyr_risksTechRiverine = QgsVectorLayer(
                (self.absPath + "/TechnicalInfrastructure_RiverineFlood_Risk.shp"),
                "TechnicalInfrastructure_RiverineFlood_RiskData",
                "ogr",
            )
            lyr_risksTechPluvial = QgsVectorLayer(
                (self.absPath + "/TechnicalInfrastructure_PluvialFlood_Risk.shp"),
                "TechnicalInfrastructure_PluvialFlood_RiskData",
                "ogr",
            )
            lyr_risksRoadsRiverine = QgsVectorLayer(
                (self.absPath + "/Roads_RiverineFlood_Risk.shp"),
                "Roads_RiverineFlood_RiskData",
                "ogr",
            )
            lyr_risksRoadsPluvial = QgsVectorLayer(
                (self.absPath + "/Roads_PluvialFlood_Risk.shp"),
                "Roads_PluvialFlood_RiskData",
                "ogr",
            )

            dfBuildRiv = self.step14.getDf(lyr_risksBuildingsRiverine)
            dfBuildRiv = self.step14.editAttributeTable(
                dfBuildRiv, "Buildings", "Riverine"
            )

            dfBuildPluv = self.step14.getDf(lyr_risksBuildingsPluvial)
            dfBuildPluv = self.step14.editAttributeTable(
                dfBuildPluv, "Buildings", "Pluvial"
            )

            dfTechRiv = self.step14.getDf(lyr_risksTechRiverine)
            dfTechRiv = self.step14.editAttributeTable(
                dfTechRiv, "TechnicalInfrastructure", "Riverine"
            )

            dfTechPluv = self.step14.getDf(lyr_risksTechPluvial)
            dfTechPluv = self.step14.editAttributeTable(
                dfTechPluv, "TechnicalInfrastructure", "Pluvial"
            )

            dfRoadsRiv = self.step14.getDf(lyr_risksRoadsRiverine)
            dfRoadsRiv = self.step14.editAttributeTable(dfRoadsRiv, "Roads", "Riverine")

            dfRoadsPluv = self.step14.getDf(lyr_risksRoadsPluvial)
            dfRoadsPluv = self.step14.editAttributeTable(
                dfRoadsPluv, "Roads", "Pluvial"
            )

            dfRisks = pd.DataFrame(
                columns=["Asset_Type", "Asset", "Flood_Type", "Risk", "Count"]
            )

            dfRisks = self.step14.createRiskDataTable(
                dfBuildRiv, dfRisks, "Buildings", "Riverine"
            )
            dfRisks = self.step14.createRiskDataTable(
                dfBuildPluv, dfRisks, "Buildings", "Pluvial"
            )
            dfRisks = self.step14.createRiskDataTable(
                dfTechRiv, dfRisks, "TechnicalInfrastructure", "Riverine"
            )
            dfRisks = self.step14.createRiskDataTable(
                dfTechPluv, dfRisks, "TechnicalInfrastructure", "Pluvial"
            )
            dfRisks = self.step14.createRiskDataTable(
                dfRoadsRiv, dfRisks, "Roads", "Riverine"
            )
            dfRisks = self.step14.createRiskDataTable(
                dfRoadsPluv, dfRisks, "Roads", "Pluvial"
            )

            # Export risk statistics as excel
            filepath = folderpath + "/riskStats.xlsx"
            dfRisks.to_excel(filepath, index=False) #index=False nötig?

            widget = iface.messageBar().createMessage("Step 14", "Exporting done!")
            iface.messageBar().pushWidget(widget, Qgis.Success)
