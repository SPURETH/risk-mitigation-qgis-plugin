# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic, QtGui
from qgis.PyQt.QtGui import QIcon
from qgis.gui import QgsAttributeTableView, QgsAttributeTableModel, QgsAttributeTableFilterModel, QgsDualView
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QToolBar, QAction, QWidget
from qgis.core import QgsVectorLayerCache, QgsEditorWidgetSetup
from qgis.PyQt.QtCore import Qt

class AttributeTableDialog(QDialog):
    """Dialog class for showing the attribute table of a vector layer. """
    
    def __init__(self, parent, canvas, layer, editable_fields):
        """Constructor method for initializing a layer attribute dialog window instance.
        
        Args:
            vectorLayer (QgsVectorLayer): a vector layer instance.
            parent: the dialog's parent instance.
        """
        super(AttributeTableDialog, self).__init__(parent)
        
        self.vectorLayer = layer
        self.canvas = canvas
        self.main = parent
        #self.dialogTitle = 'Attribute Editor - ' + self.vectorLayer.name()
        
        self.setupUi(self)

        # Configure the visible fields
        #editable_fields = ["WaterHgt", "RepeatYear"]
        self.configureAttributeForm(self.vectorLayer, editable_fields)

        self.dualView.init(self.vectorLayer, self.canvas)

        self.dualView.setView(QgsDualView.AttributeEditor)

        self.actionToggleEditLayer.triggered.connect(self.handlerToggleEditLayer)
    
    
    def setupUi(self, parent):
        """Method for building the dialog UI.
        
        Args:
            parent: the dialog's parent instance.
        """
        self.dialogLayout = QVBoxLayout(parent)
        
        self.toolBar = QToolBar(self)
        self.dialogLayout.addWidget(self.toolBar)
        
        plg_dir = os.path.dirname(__file__)

        # icons: folder containing my icon files
        icon_path = os.path.join(plg_dir, "iconEdit.png")
        icon = QIcon(icon_path)
        #icon = QIcon(':/plugins/UNHCR/iconEdit.png')
        self.actionToggleEditLayer = QAction(icon, 'Toggle Edit Layer', self)
        self.actionToggleEditLayer.setCheckable(True)
        self.toolBar.addAction(self.actionToggleEditLayer)
        
        self.dualView = QgsDualView()
        self.dialogLayout.addWidget(self.dualView)
        
        self.setLayout(self.dialogLayout)
        
        #self.setWindowTitle(self.dialogTitle)
        self.setMinimumSize(800, 400)
        self.resize(parent.sizeHint())

    def configureAttributeForm(self, layer, editable_fields):
        """Configure specific fields as editable in the attribute form."""

        # Set up the attribute form for each field
        for field in layer.fields():
            field_name = field.name()

            if field_name in editable_fields:
                # Set the widget for editable fields (e.g., a text edit)
                
                if field_name == "YrlyFlood":
                    widget_setup = QgsEditorWidgetSetup('CheckBox', {'unchecked': False})
                
                elif field_name == "Intensity" or field_name == "Hazard":
                    widget_setup = QgsEditorWidgetSetup('Range', {'Min': 1, 'Max': 3, 'Step': 1})
                    #QgsEditorWidgetSetup('ValueMap', {'map': {'Option 1': 1, 'Option 2': 2, 'Option 3': 3}})
                
                else:
                    widget_setup = QgsEditorWidgetSetup('TextEdit', {})

                
            else:
                # Hide fields you don't want to show in the form
                widget_setup = QgsEditorWidgetSetup('Hidden', {})

            # Apply the widget setup to each field
            layer.setEditorWidgetSetup(layer.fields().indexOf(field_name), widget_setup)

        # Optionally make specific fields read-only
        # read_only_fields = ["ReadOnlyField1", "ReadOnlyField2"]
        # for field_name in read_only_fields:
        #     widget_setup = QgsEditorWidgetSetup('TextEdit', {'IsReadOnly': 'True'})
        #     layer.setEditorWidgetSetup(layer.fields().indexOf(field_name), widget_setup)

        # Save the changes to the layer, so the custom form is used when editing the layer
        layer.triggerRepaint()
    
    def closeEvent(self, event):
        """Overload method that is called when the dialog widget is closed.
        
        Args:
            event (QCloseEvent): the close widget event.
        """
        ##super(DialogLayerAttributeDualView, self).closeEvent(event)

        reply = self.confirmSaveLayer()
        
        if reply == QMessageBox.Save:

            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        elif reply == QMessageBox.Cancel:
            event.ignore()
        elif reply == None:
            # Click toggle edit button => close dialog => (layer was not modified)
            self.vectorLayer.rollBack()
            self.vectorLayer.setReadOnly()
    
    
    def confirmSaveLayer(self):
        """Method for confirming saving the changes made to the layer. """
        
        reply = None
        
        if self.vectorLayer.isModified():
            reply = QMessageBox.question(
                self,
                'Save Layer Changes',
                'Do you want to save the changes made to layer {0}?'.format(self.vectorLayer.name()),
                QMessageBox.Save|QMessageBox.No|QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.vectorLayer.commitChanges() # save changes to layer
                self.vectorLayer.setReadOnly()
            elif reply == QMessageBox.No:
                self.vectorLayer.rollBack()
                self.vectorLayer.setReadOnly()
            elif reply == QMessageBox.Cancel:
                pass
            
        return reply
    
    
    def handlerToggleEditLayer(self):
        """Slot method when the edit layer button is clicked. """

        if self.actionToggleEditLayer.isChecked():
            self.vectorLayer.setReadOnly(False)
            self.vectorLayer.startEditing()
        else:
            reply = self.confirmSaveLayer()
            
            print(reply)
            
            if reply == QMessageBox.Cancel:
                self.actionToggleEditLayer.setChecked(False) # Keep toggle edit button checked
            elif reply == None:
                # Click toggle edit button => select one feature => click toggle edit button => (layer was not modified)
                self.vectorLayer.rollBack()
                self.vectorLayer.setReadOnly()

    # def configureAttributeForm(self, layer, read_only_fields):
    #     """Configure specific fields as non-editable (read-only) in the attribute form."""
    #     # Loop through all fields in the layer
    #     for field in layer.fields():
    #         field_name = field.name()
            
    #         if field_name in read_only_fields:
    #             # Set the widget to 'Label' to make it non-editable
    #             widget_setup = QgsEditorWidgetSetup('Label', {})
    #         else:
    #             # Set the widget to 'TextEdit' for editable fields
    #             widget_setup = QgsEditorWidgetSetup('TextEdit', {})
            
    #         # Apply the widget setup to the layer's field
    #         layer.setEditorWidgetSetup(layer.fields().indexOf(field_name), widget_setup)