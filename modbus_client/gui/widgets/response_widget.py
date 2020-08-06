from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class ResponseWidget(QGroupBox):

    def __init__(self):
        super(ResponseWidget, self).__init__('RESPONSE')
        self.res_message = QLabel()
        self.res_message.setAlignment(Qt.AlignCenter)
        reslayout = QVBoxLayout()
        reslayout.addWidget(self.res_message)
        self.setAlignment(Qt.AlignCenter)
        self.setLayout(reslayout)

    def update_response(self, message):
        if current_selection := message['function_code'] <= 4:
            if current_selection == 1:
                self.res_message.setText(
                    f"Coils set are: {','.join(message['status_list'])}" if len(message['status_list'])
                    else 'No coils are set')
            elif current_selection == 2:
                self.res_message.setText(
                    f"Discrete inputs status: {','.join(message['status_list'])}" if len(message['status_list'])
                    else 'No discrete inputs are set.')
            elif current_selection == 3:
                self.res_message.setText(f"Holding registers data: {','.join(message['register_data'])}")
            elif current_selection == 4:
                self.res_message.setText(f"Input registers data: {','.join(message['register_data'])}")
