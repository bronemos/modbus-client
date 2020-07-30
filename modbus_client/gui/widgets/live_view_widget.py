from PySide2 import QtCore
from PySide2.QtWidgets import *

from modbus_client.gui.widgets.read_widgets import *


class LiveViewWidget(QGroupBox):

    def __init__(self):
        super(LiveViewWidget, self).__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)
        layout = QGridLayout()
        for i in range(2):
            layout.setRowStretch(i, 1)
        for i in range(4):
            layout.setColumnStretch(i, 1)

        read_coils = QGroupBox("READ COILS")
        read_coils.setAlignment(QtCore.Qt.AlignCenter)
        read_coils_layout = QHBoxLayout()
        read_coils_layout.addWidget(ReadCoilsWidget())
        read_coils.setLayout(read_coils_layout)

        read_discrete_inputs = QGroupBox("READ DISCRETE INPUTS")
        read_discrete_inputs.setAlignment(QtCore.Qt.AlignCenter)
        read_discrete_inputs_layout = QHBoxLayout()
        read_discrete_inputs_layout.addWidget(ReadDiscreteInputsWidget())
        read_discrete_inputs.setLayout(read_discrete_inputs_layout)

        read_holding_registers = QGroupBox("READ HOLDING REGISTERS")
        read_holding_registers.setAlignment(QtCore.Qt.AlignCenter)
        read_holding_registers_layout = QHBoxLayout()
        read_holding_registers_layout.addWidget(ReadHoldingRegistersWidget())
        read_holding_registers.setLayout(read_holding_registers_layout)

        read_input_registers = QGroupBox("READ INPUT REGISTERS")
        read_input_registers.setAlignment(QtCore.Qt.AlignCenter)
        read_input_registers_layout = QHBoxLayout()
        read_input_registers_layout.addWidget(ReadInputRegistersWidget())
        read_input_registers.setLayout(read_input_registers_layout)

        read_coils_response = QGroupBox()
        read_coils_response.setAlignment(QtCore.Qt.AlignCenter)

        read_discrete_inputs_response = QGroupBox()
        read_discrete_inputs_response.setAlignment(QtCore.Qt.AlignCenter)

        read_holding_registers_response = QGroupBox()
        read_holding_registers_response.setAlignment(QtCore.Qt.AlignCenter)

        read_input_registers_response = QGroupBox()
        read_input_registers_response.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(read_coils, 0, 0)
        layout.addWidget(read_discrete_inputs, 0, 1)
        layout.addWidget(read_holding_registers, 0, 2)
        layout.addWidget(read_input_registers, 0, 3)
        layout.addWidget(read_coils_response, 1, 0)
        layout.addWidget(read_discrete_inputs_response, 1, 1)
        layout.addWidget(read_holding_registers_response, 1, 2)
        layout.addWidget(read_input_registers_response, 1, 3)

        self.setLayout(layout)
