# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.PyQt.QtCore import Qt

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_chooseOption_base.ui'))


class ChooseOptionDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for choosing type of data source. """

    def __init__(self, options, parent=None):
        """Constructor."""
        super(ChooseOptionDialog, self).__init__(parent)

        self.setupUi(self)

        self.cb_Data.addItems(options)
        #self.cb_Data.addItems(["Local", "Global"])

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

    def setText(self, text):
        self.label_Information.setText(text)
        self.label_Information.adjustSize()
        self.adjustSize()

    def chosenOption(self):
        return self.cb_Data.currentText()
