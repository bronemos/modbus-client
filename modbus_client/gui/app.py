import sys

from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets import *
from modbus_client.resources.codes import Codes


class Application(QMainWindow):
    connected = False
    transaction_id = 0

    def __init__(self, state_manager, parent=None):
        QMainWindow.__init__(self, parent)

        self.state_manager = state_manager
        self.state_manager.update.connect(self.update_gui)

        self.stackedRequestWidget = QStackedWidget()

        self.groupBox = QGroupBox()
        self.groupBox.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.stackedRequestWidget)
        self.groupBox.setLayout(layout)

        self.mainWidget = QWidget()

        self.HomeWidget = HomeWidget()
        self.HomeWidget.connect_button.clicked.connect(self._connect_disconnect)
        self.HomeWidget.historian_button.clicked.connect(self._set_center_widget)

        self.ReadCoilsWidget = ReadCoilsWidget()
        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        self.ReadInputRegistersWidget = ReadInputRegistersWidget()
        self.WriteSingleCoilWidget = WriteSingleCoilWidget()
        self.WriteSingleRegisterWidget = WriteSingleRegisterWidget()
        self.WriteMultipleRegistersWidget = WriteMultipleRegistersWidget()
        self.WriteMultipleCoilsWidget = WriteMultipleCoilsWidget()

        self.stackedRequestWidget.addWidget(self.ReadCoilsWidget)
        self.stackedRequestWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedRequestWidget.addWidget(self.ReadHoldingRegistersWidget)
        self.stackedRequestWidget.addWidget(self.ReadInputRegistersWidget)
        self.stackedRequestWidget.addWidget(self.WriteSingleCoilWidget)
        self.stackedRequestWidget.addWidget(self.WriteSingleRegisterWidget)
        self.stackedRequestWidget.addWidget(self.WriteMultipleCoilsWidget)
        self.stackedRequestWidget.addWidget(self.WriteMultipleRegistersWidget)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_request_widget)
        self.unitAddress = ClickableLineEdit('1')
        self.unitAddress.setToolTip('Unit address.\nValue between 1 and 65535')
        form.addRow('Unit address: ', self.unitAddress)
        form.addRow('Function: ', self.dropdown)
        layout.addWidget(self.HomeWidget)

        form.addRow(self.groupBox)

        self.sendButton = QPushButton('SEND')
        self.sendButton.clicked.connect(self._validate_and_queue)
        form.addRow(self.sendButton)

        self.reqWidget = QGroupBox('REQUEST')
        self.reqWidget.setEnabled(self.connected)
        self.reqWidget.setAlignment(Qt.AlignCenter)

        self.reqWidget.setLayout(form)

        self.resWidget = QGroupBox('RESPONSE')
        self.resWidget.setEnabled(self.connected)
        self.res_message = QLabel()
        self.res_message.setAlignment(Qt.AlignCenter)
        reslayout = QVBoxLayout()
        reslayout.addWidget(self.res_message)
        self.resWidget.setAlignment(Qt.AlignCenter)
        self.resWidget.setLayout(reslayout)

        self.requestLogWidget = RequestLogWidget()

        self.responseLogWidget = ResponseLogWidget()

        self.mainScrollWidget = QScrollArea()
        self.mainScrollWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.mainScrollWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mainScrollWidget.setWidgetResizable(True)

        self.reqresWidget = QWidget()
        reqresLayout = QGridLayout()
        reqresLayout.setRowStretch(0, 1)
        reqresLayout.setRowStretch(1, 1)
        reqresLayout.setColumnStretch(0, 1)
        reqresLayout.setColumnStretch(1, 1)
        reqresLayout.setRowMinimumHeight(0, 200)
        reqresLayout.setRowMinimumHeight(1, 500)
        reqresLayout.addWidget(self.reqWidget, 0, 0, 1, 1)
        reqresLayout.addWidget(self.resWidget, 0, 1, 1, -1)
        reqresLayout.addWidget(self.requestLogWidget, 1, 0, -1, 1)
        reqresLayout.addWidget(self.responseLogWidget, 1, 1, -1, -1)
        self.reqresWidget.setLayout(reqresLayout)

        self.mainScrollWidget.setWidget(self.reqresWidget)
        self.historianWidget = HistorianWidget()

        self.centerWidget = QStackedWidget()
        self.centerWidget.addWidget(self.mainScrollWidget)
        self.centerWidget.addWidget(self.historianWidget)

        layout.addWidget(self.centerWidget)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

    def _connect_disconnect(self):
        if not self.connected:
            self.HomeWidget.connect_button.setEnabled(self.connected)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Connecting...')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.connecting_movie)
            self.state_manager.run_loop()
        else:
            self.state_manager.req_queue.put('DC')
            self.update_gui('DC')

    def _change_request_widget(self):
        current = self.dropdown.currentIndex()
        self.stackedRequestWidget.setCurrentIndex(current)
        self.dropdown.setCurrentIndex(current)

    def _set_center_widget(self):
        if self.centerWidget.currentIndex() == 0:
            self.centerWidget.setCurrentIndex(1)
            self.historianWidget.load(self.state_manager.db)
        else:
            self.centerWidget.setCurrentIndex(0)

    def _validate_and_queue(self):
        try:
            unit_address = int(self.unitAddress.text())
        except ValueError:
            ErrorDialog(self, 'Incorrect unit address value.')
            return

        if not self.stackedRequestWidget.currentWidget().validate_input(self):
            return

        message = self.stackedRequestWidget.currentWidget().generate_message(self.transaction_id, unit_address)
        self.requestLogWidget.update_log(message)

        print(message)
        self.transaction_id += 1
        self.state_manager.req_queue.put(message)

    def update_gui(self, message):
        print('this is msg', message)
        if message == 'ACK':
            self.connected = True
            self.HomeWidget.connect_button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Disconnect')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.connected_movie)
            return
        elif message == 'DC' or message == 1000:
            self.connected = False
            self.HomeWidget.connect_button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Connect')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.disconnected_movie)
            return
        self.responseLogWidget.update_log(message)
        current_selection = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value
        if current_selection == 1:
            self.res_message.setText(f"Coils set are: {','.join(message['set_list'])}" if len(message['set_list'])
                                     else 'No coils are set')
        elif current_selection == 2:
            self.res_message.setText(
                f"Discrete inputs status: {','.join(message['set_list'])}" if len(message['set_list'])
                else 'No discrete inputs are set.')
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
