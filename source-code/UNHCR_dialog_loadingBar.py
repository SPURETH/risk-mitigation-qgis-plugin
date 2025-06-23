# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import qApp
import time

class UploadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, upload_operation):
        super(UploadThread, self).__init__()
        self.upload_operation = upload_operation

    def run(self):
        # Execute the provided upload operation
        self.result = self.upload_operation()

        # Emit the finished signal along with the result
        self.finished.emit()

class LoadingBar:
    def __init__(self, text):
        self.progress_dialog = None
        self.upload_thread = None
        self.result = None
        self.text = text
        
    def upload_file_operation(self, uploadFunction):
        self.upload_file = uploadFunction

        # Create and configure the progress dialog with indeterminate mode
        self.progress_dialog = QProgressDialog(self.text, "Cancel", 0, 0) # "Uploading..."
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setRange(0, 0)  # Set indeterminate mode

        # Connect the canceled signal to the cancel_upload function
        self.progress_dialog.canceled.connect(self.cancel_upload)

        # Start the upload process in a separate thread with the upload_file() function as a parameter
        self.upload_thread = UploadThread(upload_operation=self.upload_file)
        self.upload_thread.finished.connect(self.upload_finished)
        self.upload_thread.start()

        # Call exec() on the progress dialog to make it visible
        self.progress_dialog.exec_()

    def cancel_upload(self):
        # This function is called when the user clicks the "Cancel" button
        if self.upload_thread.isRunning():
            self.upload_thread.requestInterruption()

    def upload_finished(self):
        # This function is called when the upload process is complete
        self.progress_dialog.reset()  # This will close the progress dialog

        self.result = self.upload_thread.result

    def close(self):
        self.progress_dialog.close()
