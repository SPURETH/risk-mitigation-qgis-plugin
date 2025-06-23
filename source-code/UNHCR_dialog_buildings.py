# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.PyQt.QtCore import Qt

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_buildings_base.ui'))

class BuildingsDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for chaning Type & Construction of existing Buildings. """

    def __init__(self, text, parent=None):
        """Constructor."""

        super(BuildingsDialog, self).__init__(parent)

        self.setupUi(self)

        self.label_Information.setText(text)

        self.cb_Building_Construction.addItems(['emergency', 'transitional', 'durable'])
        self.cb_Building_Type.addItems(['ResidentialShelters', 'SocialInfrastructure', 'AdministrativeBuildings', 'Logistics', 'OpenSpaces'])

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

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

    def type(self):
        return self.cb_Building_Type.currentText()
    
    def construction(self):
        return self.cb_Building_Construction.currentText()
