# -*- coding: utf-8 -*-

from qgis.core import QgsProject, QgsPrintLayout, QgsReadWriteContext
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from PyQt5.QtCore import QEventLoop

class LayoutManager:
    def __init__(self, layout, iface):
        # Initialize the class and create the layout

        self.layout = layout
        self.iface = iface

        self.layoutDesigner = self.iface.openLayoutDesigner(self.layout)

        #self.layoutDesigner.layoutExported.connect(self.on_layout_exported)

        self.run_event_loop()
        # https://chatgpt.com/c/66e30718-3740-8001-9197-34bf0c18b41e

    def run_event_loop(self):
        """Run an event loop until the layoutExported signal is emitted."""
        event_loop = QEventLoop()

        # Connect the layoutExported signal to quit the event loop when it's emitted
        self.layoutDesigner.layoutExported.connect(event_loop.quit)

        # Start the event loop, this will block further execution until the signal is emitted
        print("Waiting for layout to be exported...")
        event_loop.exec_()

        # Once the event loop exits, continue with your process
        self.on_layout_exported()

    def on_layout_exported(self):
        """Handle the signal emitted when the layout is exported."""
        
        print('test')

        # reply = QMessageBox.question(None, 'Save Layout', 
        #                             'Do you want to save changes and export to PDF?', 
        #                             QMessageBox.Yes | QMessageBox.No)

        # if reply == QMessageBox.Yes:
        #     self.export_layout_as_pdf()

    def export_layout_as_pdf(self):
        """Export the current layout to a PDF file."""
        pdf_path = self.absPath + "/MyLayoutExport.pdf"
        exporter = QgsLayoutExporter(self.layout)
        result = exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())

        if result == QgsLayoutExporter.Success:
            print(f"Layout successfully exported to {pdf_path}")
        else:
            print("Error exporting layout to PDF")

    #     self.project = QgsProject.instance()
    #     #self.project = project
    #     self.iface = iface

    #     self.absPath = self.project.absolutePath()

    #     self.layout = QgsPrintLayout(self.project)
    #     self.layout.setName("MyLayout")
    #     self.project.layoutManager().addLayout(self.layout)

    #     # Load the QPT template
    #     qpt_file_path = self.absPath + "/Test_LayoutTemplate.qpt"
    #     with open(qpt_file_path, 'r') as f:
    #         template_content = f.read()

    #     doc = QDomDocument()
    #     doc.setContent(template_content)
    #     self.layout.loadFromTemplate(doc, QgsReadWriteContext())

    #     # Open the Layout Designer and connect the signal
    #     self.layout_designer = self.iface.openLayoutDesigner(self.layout)
    #     self.layout_designer.exec_()

    #     self.continue_processing()
    #     #self.layout_designer.closed.connect(self.on_designer_closed)

    # def on_designer_closed(self):
    #     """Slot that gets triggered when the Layout Designer is closed."""
    #     print("Layout Designer closed. Continuing with the script...")
    #     self.continue_processing()

    # def continue_processing(self):
    #     """Continue with the rest of the script after the designer is closed."""
    #     # Add your further processing code here
    #     print("Performing further processing...")

    # def closeEvent(self, event):

    #     print('closed')
