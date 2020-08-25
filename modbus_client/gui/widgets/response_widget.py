import os

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import *

from modbus_client.gui.widgets.live_response_widget import LiveResponseWidget
from modbus_client.resources.codes import ErrorCodes


class ResponseWidget(QGroupBox):

    def __init__(self):
        super(ResponseWidget, self).__init__('RESPONSE')
        self.response = LiveResponseWidget()

        self.response_widget = QWidget()
        widget_layout = QVBoxLayout()
        self.response_label = QLabel()
        self.response_image = QLabel()
        self.response_image.setAlignment(Qt.AlignCenter)
        widget_layout.addWidget(self.response_image)
        widget_layout.addWidget(self.response_label)
        self.response_widget.setLayout(widget_layout)
        path = os.path.abspath(__file__ + '/../../../resources')
        self.success = QPixmap(path + '/success1.png')
        self.error = QPixmap(path + '/error.png')
        self.response_label.setAlignment(Qt.AlignCenter)
        self.reslayout = QStackedLayout()
        self.reslayout.addWidget(self.response_widget)
        self.reslayout.addWidget(self.response)
        self.setAlignment(Qt.AlignCenter)
        self.setLayout(self.reslayout)

    def update_response(self, message):
        if message['function_code'] <= 4:
            self.response.refresh(message)
            self.reslayout.setCurrentWidget(self.response)
        elif message['function_code'] in [item.value for item in ErrorCodes]:
            self.response_image.setPixmap(self.error.scaled(50, 50, Qt.KeepAspectRatio))
            error_code = int.from_bytes(message['raw_data'], 'little')
            if error_code == 1:
                self.response_label.setText('Error!\n\nIllegal function!')
            elif error_code == 2:
                self.response_label.setText('Error!\n\nIllegal data address!')
            elif error_code == 3:
                self.response_label.setText('Error!\n\nIllegal data value!')
            else:
                self.response_label.setText('Error!\n\nSlave device failure!')
            self.response_label.setStyleSheet('color: rgb(240, 0, 0); font-weight: 500')
            self.reslayout.setCurrentWidget(self.response_widget)
        else:
            self.response_image.setPixmap(self.success.scaled(50, 50, Qt.KeepAspectRatio))
            self.response_label.setStyleSheet('color: rgb(119, 188, 31); font-weight: 500')
            self.response_label.setText('Success!')
            self.reslayout.setCurrentWidget(self.response_widget)
