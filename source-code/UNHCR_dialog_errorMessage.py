# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialogButtonBox

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_errorMessage_base.ui'))

class ErrorMessageDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for displaying error messages. """

    def __init__(self, parent=None):
        """Constructor."""
        super(ErrorMessageDialog, self).__init__(parent)

        self.setupUi(self)

    def setText(self, textError, textHint):
        self.label_Information_error.setText(textError)
        self.label_Information_hint.setText(textHint)

    def closeEvent(self, event):
        # Perform actions specific to window close button
        super().closeEvent(event)
