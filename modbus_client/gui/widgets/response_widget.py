from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from modbus_client.gui.widgets.live_response_widget import LiveResponseWidget
from modbus_client.resources.codes import Codes


class ResponseWidget(QGroupBox):

    def __init__(self):
        super(ResponseWidget, self).__init__('RESPONSE')
        self.response = LiveResponseWidget()
        reslayout = QVBoxLayout()
        reslayout.addWidget(self.response)
        self.setAlignment(Qt.AlignCenter)
        self.setLayout(reslayout)

    def update_response(self, message):
        if message['function_code'] <= 4:
            self.response.refresh(message)

    def update_response_old(self, message):
        if (current_selection := message['function_code']) <= 4:
            if current_selection == Codes.READ_COILS.value:
                self.res_message.setText(
                    f"Coils set are: {','.join(str(x) for x in message['status_list'])}" if len(message['status_list'])
                    else 'No coils are set')
            elif current_selection == Codes.READ_DISCRETE_INPUTS.value:
                self.res_message.setText(
                    f"Discrete inputs status: {','.join(str(x) for x in message['status_list'])}" if len(
                        message['status_list'])
                    else 'No discrete inputs are set.')
            elif current_selection == Codes.READ_HOLDING_REGISTERS.value:
                self.res_message.setText(f"Holding registers data: {','.join(message['register_data'])}")
            elif current_selection == Codes.READ_INPUT_REGISTERS.value:
                self.res_message.setText(f"Input registers data: {','.join(message['register_data'])}")
