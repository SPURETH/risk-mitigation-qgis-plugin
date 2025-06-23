# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialogButtonBox

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_message_base.ui'))


class MessageDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for displaying messages. """

    def __init__(self, parent=None):
        """Constructor."""
        super(MessageDialog, self).__init__(parent)

        self.setupUi(self)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.handle_accepted)
        button_box.rejected.connect(self.handle_rejected)

    def setText(self, text):
        self.label_Information.setText(text)
        self.label_Information.adjustSize()
        self.adjustSize()

    def handle_accepted(self):
        # Perform actions specific to OK button
        self.accept()

    def handle_rejected(self):
        # Perform actions specific to Cancel button
        self.reject()

    def closeEvent(self, event):
        # Perform actions specific to window close button
        super().closeEvent(event)
