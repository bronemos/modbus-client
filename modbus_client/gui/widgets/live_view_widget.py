from PySide2 import QtCore
from PySide2.QtCore import Signal
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import FancySlider
from modbus_client.gui.widgets.live_response_widget import LiveResponseWidget
from modbus_client.gui.widgets.read_widgets import *
from modbus_client.resources.codes import Codes


class LiveViewWidget(QGroupBox):
    live_error = Signal(bool)

    def __init__(self, req_queue):
        super(LiveViewWidget, self).__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)

        self.req_queue = req_queue

        layout = QGridLayout()
        for i in range(2):
            layout.setRowStretch(i, 1)
        for i in range(4):
            layout.setColumnStretch(i, 1)

        read_coils = QGroupBox('READ COILS')
        read_coils.setAlignment(QtCore.Qt.AlignCenter)
        read_coils_layout = QVBoxLayout()

        self.ReadCoilsWidget = ReadCoilsWidget()
        read_coils_layout.addWidget(self.ReadCoilsWidget)

        self.ReadCoilsResponse = LiveResponseWidget()
        read_coils_layout.addWidget(self.ReadCoilsResponse)
        read_coils.setLayout(read_coils_layout)

        read_discrete_inputs = QGroupBox('READ DISCRETE INPUTS')
        read_discrete_inputs.setAlignment(QtCore.Qt.AlignCenter)
        read_discrete_inputs_layout = QVBoxLayout()

        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        read_discrete_inputs_layout.addWidget(self.ReadDiscreteInputsWidget)

        self.ReadDiscreteInputsResponse = LiveResponseWidget()
        read_discrete_inputs_layout.addWidget(self.ReadDiscreteInputsResponse)
        read_discrete_inputs.setLayout(read_discrete_inputs_layout)

        read_holding_registers = QGroupBox('READ HOLDING REGISTERS')
        read_holding_registers.setAlignment(QtCore.Qt.AlignCenter)
        read_holding_registers_layout = QVBoxLayout()

        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        read_holding_registers_layout.addWidget(self.ReadHoldingRegistersWidget)

        self.ReadHoldingRegistersResponse = LiveResponseWidget()
        read_holding_registers_layout.addWidget(self.ReadHoldingRegistersResponse)
        read_holding_registers.setLayout(read_holding_registers_layout)

        read_input_registers = QGroupBox('READ INPUT REGISTERS')
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

        self.fancy_slider = FancySlider(1, 60, 3)
        self.fancy_slider.slider.valueChanged.connect(self.update_slider)

        layout.addWidget(read_coils, 0, 0)
        layout.addWidget(read_discrete_inputs, 0, 1)
        layout.addWidget(read_holding_registers, 0, 2)
        layout.addWidget(read_input_registers, 0, 3)
        layout.addWidget(self.progressBar, 1, 0, 1, -1)
        layout.addWidget(self.fancy_slider, 2, 1, 1, 2)

        self.setLayout(layout)

    def update_view_request(self):
        if self.ReadCoilsWidget.validate_input(self):
            read_coils_message = self.ReadCoilsWidget.generate_message()
            read_coils_message['user_generated'] = False
            self.req_queue.put(read_coils_message)
        else:
            self.req_queue.put('pause_refresh')
            self.fancy_slider.pause_button.setChecked(False)
        if self.ReadDiscreteInputsWidget.validate_input(self):
            read_discrete_inputs_message = self.ReadDiscreteInputsWidget.generate_message()
            read_discrete_inputs_message['user_generated'] = False
            self.req_queue.put(read_discrete_inputs_message)
        else:
            self.req_queue.put('pause_refresh')
            self.fancy_slider.pause_button.setChecked(False)
        if self.ReadHoldingRegistersWidget.validate_input(self):
            read_holding_registers_message = self.ReadHoldingRegistersWidget.generate_message()
            read_holding_registers_message['user_generated'] = False
            self.req_queue.put(read_holding_registers_message)
        else:
            self.req_queue.put('pause_refresh')
            self.fancy_slider.pause_button.setChecked(False)
        if self.ReadInputRegistersWidget.validate_input(self):
            read_input_registers_message = self.ReadInputRegistersWidget.generate_message()
            read_input_registers_message['user_generated'] = False
            self.req_queue.put(read_input_registers_message)
        else:
            self.req_queue.put('pause_refresh')
            self.fancy_slider.pause_button.setChecked(False)

    def update_view(self, message):
        if message['function_code'] == Codes.READ_COILS.value:
            self.ReadCoilsResponse.refresh(message)
        elif message['function_code'] == Codes.READ_DISCRETE_INPUTS.value:
            self.ReadDiscreteInputsResponse.refresh(message)
        elif message['function_code'] == Codes.READ_HOLDING_REGISTERS.value:
            self.ReadHoldingRegistersResponse.refresh(message)
        else:
            self.ReadInputRegistersResponse.refresh(message)

    def update_slider(self):
        self.req_queue.put(self.fancy_slider.slider.value())
        self.fancy_slider.curr_value.setText(str(self.fancy_slider.slider.value()) + 's')
