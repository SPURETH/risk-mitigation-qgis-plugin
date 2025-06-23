# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.core import QgsProject

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_fieldPresent_base.ui'))


class FieldPresentDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for adjusting risks. """

    def __init__(self, message, layer, parent=None):
        """Constructor."""
        super(FieldPresentDialog, self).__init__(parent)
      
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.label_Information.setText(message)

        fieldNames = [field.name() for field in layer.fields()]
        self.cb_Field.addItems(fieldNames)

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

    def getField(self):
        return self.cb_Field.currentText()


