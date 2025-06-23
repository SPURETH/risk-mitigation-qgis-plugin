# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UNHCR_dialog_message_base_yesno.ui'))


class MessageDialogYesNo(QtWidgets.QDialog, FORM_CLASS):
    """Dialog class for displaying messages. """

    def __init__(self, parent=None):
        """Constructor."""
        super(MessageDialogYesNo, self).__init__(parent)

        self.setupUi(self)

        self.resultStr = None
        self.clicked_button_text = None

        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        #button_box.button(QDialogButtonBox.Yes).clicked.connect(self.handle_yes)
        #button_box.button(QDialogButtonBox.No).clicked.connect(self.handle_no)

        # button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject_cancel)

        #button_box.accepted.connect(self.handle_yes)
        #button_box.rejected.connect(self.handle_no)
        #button_box.button(QDialogButtonBox.No).clicked.connect(self.reject_no)

        button_box.clicked.connect(self.handle_button_click)

    def setText(self, text):
        self.label_Information.setText(text)
        self.label_Information.adjustSize()
        self.adjustSize()

    def handle_yes(self):
        self.resultStr = "Yes"
        self.accept()

    def handle_no(self):
        self.resultStr = "No"
        self.reject()

    def handle_button_click(self, button):
        self.clicked_button_text = button.text()

        if self.clicked_button_text == "Yes":
            self.accept()  # Close with QDialog.Accepted
        elif self.clicked_button_text == "No":
            self.reject()

    def closeEvent(self, event):
        # Perform actions specific to window close button
        self.resultStr = "Close"
        super().closeEvent(event)
        #event.accept()
        #self.close()
