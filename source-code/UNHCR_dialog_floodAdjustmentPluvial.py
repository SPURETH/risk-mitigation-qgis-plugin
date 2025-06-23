# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_floodAdjustmentPluvial_base.ui'))


class FloodAdjustmentPluvialDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for adjusting return period and intensity of flood area. """

    def __init__(self, message, parent=None):
        """Constructor."""
        super(FloodAdjustmentPluvialDialog, self).__init__(parent)

        self.setupUi(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.label_Information.setText(message)

        self.cb_Intensity_Riverine.addItems([str(1), str(2), str(3)])

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

    def getInsentity(self):
        return int(self.cb_Intensity_Riverine.currentText())


