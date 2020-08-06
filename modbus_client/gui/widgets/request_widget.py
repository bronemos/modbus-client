from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from modbus_client.gui.widgets.read_widgets import *
from modbus_client.gui.widgets.write_widgets import *
from modbus_client.resources.codes import Codes


class RequestWidget(QGroupBox):

    def __init__(self):
        super(RequestWidget, self).__init__("REQUEST")
        self.stackedRequestWidget = QStackedWidget()
        self.setAlignment(Qt.AlignCenter)

        self.ReadCoilsWidget = ReadCoilsWidget()
        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        self.ReadInputRegistersWidget = ReadInputRegistersWidget()
        self.WriteSingleCoilWidget = WriteSingleCoilWidget()
        self.WriteSingleRegisterWidget = WriteSingleRegisterWidget()
        self.WriteMultipleRegistersWidget = WriteMultipleRegistersWidget()
        self.WriteMultipleCoilsWidget = WriteMultipleCoilsWidget()

        self.stackedRequestWidget.addWidget(self.WriteSingleCoilWidget)
        self.stackedRequestWidget.addWidget(self.WriteSingleRegisterWidget)
        self.stackedRequestWidget.addWidget(self.WriteMultipleCoilsWidget)
        self.stackedRequestWidget.addWidget(self.WriteMultipleRegistersWidget)
        self.stackedRequestWidget.addWidget(self.ReadCoilsWidget)
        self.stackedRequestWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedRequestWidget.addWidget(self.ReadHoldingRegistersWidget)
        self.stackedRequestWidget.addWidget(self.ReadInputRegistersWidget)
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_request_widget)
        form.addRow('Function: ', self.dropdown)

        self.groupBox = QGroupBox()
        self.groupBox.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.stackedRequestWidget)
        self.groupBox.setLayout(layout)

        form.addRow(self.groupBox)
        self.sendButton = QPushButton('SEND')
        form.addRow(self.sendButton)

        self.setLayout(form)

    def _change_request_widget(self):
        current = self.dropdown.currentIndex()
        self.stackedRequestWidget.setCurrentIndex(current)
        self.dropdown.setCurrentIndex(current)


