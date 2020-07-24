import sys
from concurrent.futures import ThreadPoolExecutor

from modbus_client.codes import Codes
from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets import *

protocol_code = '0000'


class Application(QMainWindow):
    executor = ThreadPoolExecutor(max_workers=1)
    connected = False
    message_id = 0

    def __init__(self, state_manager, parent=None):
        QMainWindow.__init__(self, parent)

        self.state_manager = state_manager
        self.state_manager.update.connect(self.update_gui)

        self.stackedMainWidget = QStackedWidget()

        self.groupBox = QGroupBox()
        self.groupBox.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.stackedMainWidget)
        self.groupBox.setLayout(layout)

        self.mainWidget = QWidget()

        self.ConnectWidget = HomeWidget()
        self.ConnectWidget.connect_button.clicked.connect(self._connect_disconnect)

        self.ReadCoilsWidget = ReadCoilsWidget()
        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        self.ReadInputRegistersWidget = ReadInputRegistersWidget()
        self.WriteSingleCoilWidget = WriteSingleCoilWidget()
        self.WriteSingleRegisterWidget = WriteSingleRegisterWidget()
        self.WriteMultipleRegistersWidget = WriteMultipleRegistersWidget()
        self.WriteMultipleCoilsWidget = WriteMultipleCoilsWidget()

        self.stackedMainWidget.addWidget(self.ReadCoilsWidget)
        self.stackedMainWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedMainWidget.addWidget(self.ReadHoldingRegistersWidget)
        self.stackedMainWidget.addWidget(self.ReadInputRegistersWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleCoilWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleRegisterWidget)
        self.stackedMainWidget.addWidget(self.WriteMultipleCoilsWidget)
        self.stackedMainWidget.addWidget(self.WriteMultipleRegistersWidget)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_widget)
        self.unitAddress = ClickableLineEdit('1')
        self.unitAddress.setToolTip("Unit address.\nValue between 1 and 65535")
        form.addRow("Unit address: ", self.unitAddress)
        form.addRow("Function: ", self.dropdown)
        layout.addWidget(self.ConnectWidget)

        form.addRow(self.groupBox)

        self.sendButton = QPushButton("SEND")
        self.sendButton.clicked.connect(self._validate_and_queue)
        form.addRow(self.sendButton)

        self.reqWidget = QGroupBox("REQUEST")
        self.reqWidget.setEnabled(self.connected)
        self.reqWidget.setAlignment(Qt.AlignCenter)

        self.reqWidget.setLayout(form)

        self.resWidget = QGroupBox("RESPONSE")
        self.resWidget.setEnabled(self.connected)
        self.res_message = QLabel()
        self.res_message.setAlignment(Qt.AlignCenter)
        reslayout = QVBoxLayout()
        reslayout.addWidget(self.res_message)
        self.resWidget.setAlignment(Qt.AlignCenter)
        self.resWidget.setLayout(reslayout)

        self.requestLogWidget = RequestLogWidget()

        self.responseLogWidget = ResponseLogWidget()

        self.reqresWidget = QWidget()
        reqresLayout = QGridLayout()
        reqresLayout.setRowStretch(0, 1)
        reqresLayout.setRowStretch(1, 1)
        reqresLayout.setColumnStretch(0, 1)
        reqresLayout.setColumnStretch(1, 1)
        reqresLayout.addWidget(self.reqWidget, 0, 0, 1, 1)
        reqresLayout.addWidget(self.resWidget, 0, 1, 1, -1)
        reqresLayout.addWidget(self.requestLogWidget, 1, 0, -1, 1)
        reqresLayout.addWidget(self.responseLogWidget, 1, 1, -1, -1)
        self.reqresWidget.setLayout(reqresLayout)
        # layout.addWidget(self.reqWidget)

        layout.addWidget(self.reqresWidget)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

    def _connect_disconnect(self):
        if not self.connected:
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.connecting_movie)
            self.ConnectWidget.connect_button.setText("Connecting...")
            self.ConnectWidget.connect_button.setEnabled(False)
        else:
            self.state_manager.req_queue.put("DC")

            self.connected = False
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.ConnectWidget.connect_button.setText("Connect")
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.disconnected_movie)

    def _change_widget(self):
        current = self.dropdown.currentIndex()
        self.stackedMainWidget.setCurrentIndex(current)
        self.dropdown.setCurrentIndex(current)

    def _validate_and_queue(self):
        try:
            unit_address = int(self.unitAddress.text())
        except ValueError:
            ErrorDialog(self, "Incorrect unit address value.")
            return

        if not self.stackedMainWidget.currentWidget().validate_input(self):
            return

        message = self.stackedMainWidget.currentWidget().generate_message(self.message_id, unit_address)
        self.requestLogWidget.update_log(message)

        print(message)
        self.message_id += 1
        self.state_manager.req_queue.put(message)
        # asyncio.new_event_loop().run_until_complete(self.show_response())

    def update_gui(self, message):
        print(message)
        if message == 'ACK':
            self.connected = True
            self.ConnectWidget.connect_button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.ConnectWidget.connect_button.setText("Disconnect")
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.connected_movie)

        else:
            self.ConnectWidget.connect_button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.ConnectWidget.connect_button.setText("Connect")
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.disconnected_movie)
        self.responseLogWidget.update_log(message)
        current_selection = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value
        if current_selection == 1:
            self.res_message.setText(f"Coils set are: {','.join(message['set_list'])}" if len(message['set_list'])
                                     else "No coils are set")
        elif current_selection == 2:
            self.res_message.setText(
                f"Discrete inputs status: {','.join(message['set_list'])}" if len(message['set_list'])
                else "No discrete inputs are set.")
        elif current_selection == 3:
            self.res_message.setText(f"Holding registers data: {','.join(message['register_data'])}")
        elif current_selection == 4:
            self.res_message.setText(f"Input registers data: {','.join(message['register_data'])}")


def run_gui(state_manager):
    app = QApplication()
    app.setApplicationDisplayName('Modbus Client GUI')
    app.setStyle('fusion')
    mainWindow = Application(state_manager)
    p = mainWindow.palette()
    p.setColor(mainWindow.backgroundRole(), Qt.white)
    mainWindow.setPalette(p)
    mainWindow.setMinimumSize(1400, 800)
    mainWindow.show()
    sys.exit(app.exec_())
