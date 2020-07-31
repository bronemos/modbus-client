from PySide2 import QtCore
from PySide2.QtWidgets import *

from modbus_client.gui.widgets.live_response_widget import LiveResponseWidget
from modbus_client.gui.widgets.read_widgets import *
from modbus_client.state_manager.counter import Counter


class LiveViewWidget(QGroupBox):

    def __init__(self, req_queue):
        super(LiveViewWidget, self).__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)

        self.req_queue = req_queue

        layout = QGridLayout()
        for i in range(2):
            layout.setRowStretch(i, 1)
        for i in range(4):
            layout.setColumnStretch(i, 1)

        read_coils = QGroupBox("READ COILS")
        read_coils.setAlignment(QtCore.Qt.AlignCenter)
        read_coils_layout = QVBoxLayout()

        self.ReadCoilsWidget = ReadCoilsWidget()
        read_coils_layout.addWidget(self.ReadCoilsWidget)

        self.ReadCoilsResponse = LiveResponseWidget()
        read_coils_layout.addWidget(self.ReadCoilsResponse)
        read_coils.setLayout(read_coils_layout)

        read_discrete_inputs = QGroupBox("READ DISCRETE INPUTS")
        read_discrete_inputs.setAlignment(QtCore.Qt.AlignCenter)
        read_discrete_inputs_layout = QVBoxLayout()

        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        read_discrete_inputs_layout.addWidget(self.ReadDiscreteInputsWidget)

        self.ReadDiscreteInputsResponse = LiveResponseWidget()
        read_discrete_inputs_layout.addWidget(self.ReadDiscreteInputsResponse)
        read_discrete_inputs.setLayout(read_discrete_inputs_layout)

        read_holding_registers = QGroupBox("READ HOLDING REGISTERS")
        read_holding_registers.setAlignment(QtCore.Qt.AlignCenter)
        read_holding_registers_layout = QVBoxLayout()

        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        read_holding_registers_layout.addWidget(self.ReadHoldingRegistersWidget)

        self.ReadHoldingRegistersResponse = LiveResponseWidget()
        read_holding_registers_layout.addWidget(self.ReadHoldingRegistersResponse)
        read_holding_registers.setLayout(read_holding_registers_layout)

        read_input_registers = QGroupBox("READ INPUT REGISTERS")
        read_input_registers.setAlignment(QtCore.Qt.AlignCenter)
        read_input_registers_layout = QVBoxLayout()

        self.ReadInputRegistersWidget = ReadInputRegistersWidget()
        read_input_registers_layout.addWidget(self.ReadInputRegistersWidget)

        self.ReadInputRegistersResponse = LiveResponseWidget()
        read_input_registers_layout.addWidget(self.ReadInputRegistersResponse)
        read_input_registers.setLayout(read_input_registers_layout)

        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setTextVisible(False)
        self.counter = Counter()
        self.counter.update_counter.connect(self.progressBar.setValue)
        self.counter.update_live_view.connect(self.update_view_request)

        layout.addWidget(read_coils, 0, 0)
        layout.addWidget(read_discrete_inputs, 0, 1)
        layout.addWidget(read_holding_registers, 0, 2)
        layout.addWidget(read_input_registers, 0, 3)
        layout.addWidget(self.progressBar, 1, 0, -1, -1)

        self.setLayout(layout)

    def update_view_request(self):
        if self.ReadCoilsWidget.validate_input(self) and \
                self.ReadDiscreteInputsWidget.validate_input(self) and \
                self.ReadHoldingRegistersWidget.validate_input(self) and \
                self.ReadInputRegistersWidget.validate_input(self):
            self.req_queue.put(self.ReadCoilsWidget.generate_message(0))
            self.req_queue.put(self.ReadDiscreteInputsWidget.generate_message(1))
            self.req_queue.put(self.ReadHoldingRegistersWidget.generate_message(2))
            self.req_queue.put(self.ReadInputRegistersWidget.generate_message(3))

    def update_view(self, message):
        if message['transaction_id'] == 0:
            self.ReadCoilsResponse.refresh(message)
        elif message['transaction_id'] == 1:
            self.ReadDiscreteInputsResponse.refresh(message)
        elif message['transaction_id'] == 2:
            self.ReadHoldingRegistersResponse.refresh(message)
        else:
            self.ReadInputRegistersResponse.refresh(message)


