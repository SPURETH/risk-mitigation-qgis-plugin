# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.core import QgsProject

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_riskAdjustment_base.ui'))


class RiskAdjustmentDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for adjusting risks. """

    def __init__(self, message, parent=None):
        """Constructor."""
        super(RiskAdjustmentDialog, self).__init__(parent)
      
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.label_Information.setText(message)

        self.cb_Layer.addItems(['Buildings Riverine', 'Buildings Pluvial', 'Roads Riverine', 'Roads Pluvial','Technical Infrastructure Riverine', 'Technical Infrastructure Pluvial', ])
        self.cb_Risk.addItems([str(1), str(2), str(3), str(4), str(5)])

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.handle_accepted)
        button_box.rejected.connect(self.handle_rejected)

    def handle_accepted(self):
        # Perform actions specific to OK button
        self.accept()
        #self.step1.drawCamp()

    def handle_rejected(self):
        # Perform actions specific to Cancel button
        self.reject()

    def closeEvent(self, event):
        # Perform actions specific to window close button
        super().closeEvent(event)

    def getLayer(self):

        textLayer = self.cb_Layer.currentText()

        if textLayer == 'Buildings Riverine':
            layer = QgsProject.instance().mapLayersByName("Buildings_RiverineFlood_Risk")[0]
        elif textLayer == 'Buildings Pluvial': 
            layer = QgsProject.instance().mapLayersByName("Buildings_PluvialFlood_Risk")[0]
        elif textLayer == 'Roads Riverine':
            layer = QgsProject.instance().mapLayersByName("Roads_RiverineFlood_Risk")[0]
        elif textLayer == 'Roads Pluvial': 
            layer = QgsProject.instance().mapLayersByName("Roads_PluvialFlood_Risk")[0]
        elif textLayer == 'Technical Infrastructure Riverine':
            layer = QgsProject.instance().mapLayersByName("TechnicalInfrastructure_RiverineFlood_Risk")[0]
        elif textLayer == 'Technical Infrastructure Pluvial': 
            layer = QgsProject.instance().mapLayersByName("TechnicalInfrastructure_PluvialFlood_Risk")[0]

        return layer

    def getRisk(self):
        return int(self.cb_Risk.currentText())


