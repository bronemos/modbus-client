from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets import *
from modbus_client.gui.widgets import RequestWidget
from modbus_client.resources.codes import Codes


class Application(QMainWindow):
    connected = False
    transaction_id = 128

    def __init__(self, state_manager, parent=None):
        QMainWindow.__init__(self, parent)

        self.state_manager = state_manager
        self.state_manager.update.connect(self.update_gui)

        self.mainWidget = QWidget()

        self.HomeWidget = HomeWidget()
        self.HomeWidget.connect_button.clicked.connect(self._connect_disconnect)
        self.HomeWidget.historian_button.clicked.connect(self._switch_to_historian)
        self.HomeWidget.historian_popup.clicked.connect(self._switch_to_historian_popup)
        self.HomeWidget.live_button.clicked.connect(self._switch_to_live)
        self.HomeWidget.live_popup.clicked.connect(self._switch_to_live_popup)

        layout = QVBoxLayout()
        layout.addWidget(self.HomeWidget)

        self.reqWidget = RequestWidget()
        self.reqWidget.setEnabled(self.connected)
        self.reqWidget.sendButton.clicked.connect(self._validate_and_queue)

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

        self.historianWidget = HistorianWidget()
        p = self.historianWidget.palette()
        p.setColor(self.historianWidget.backgroundRole(), Qt.white)
        self.historianWidget.setPalette(p)
        self.liveViewWidget = LiveViewWidget(self.state_manager.req_queue)
        self.state_manager.update_counter.connect(self.liveViewWidget.progressBar.setValue)
        self.state_manager.update_view.connect(self.liveViewWidget.update_view_request)
        p = self.liveViewWidget.palette()
        p.setColor(self.liveViewWidget.backgroundRole(), Qt.white)
        self.liveViewWidget.setPalette(p)
        self.liveViewWidget.setEnabled(self.connected)

        self.centerWidget = QStackedWidget()
        self.centerWidget.addWidget(self.reqresWidget)
        self.centerWidget.addWidget(self.historianWidget)
        self.centerWidget.addWidget(self.liveViewWidget)

        layout.addWidget(self.centerWidget)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

    def _connect_disconnect(self):
        if not self.connected:
            self.HomeWidget.connect_button.setEnabled(False)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.liveViewWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Connecting...')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.connecting_movie)
            self.state_manager.run_loop()
        else:
            self.state_manager.req_queue.put('DC')
            self.update_gui('DC')

    def _switch_to_historian(self):
        if self.centerWidget.currentWidget() != self.historianWidget:
            self.historianWidget.load(self.state_manager.db)
            self.centerWidget.addWidget(self.historianWidget)
            self.centerWidget.setCurrentWidget(self.historianWidget)
        else:
            self.centerWidget.setCurrentWidget(self.reqresWidget)

    def _switch_to_live(self):
        if self.centerWidget.currentWidget() != self.liveViewWidget:
            self.centerWidget.addWidget(self.liveViewWidget)
            self.centerWidget.setCurrentWidget(self.liveViewWidget)
        else:
            self.centerWidget.setCurrentWidget(self.reqresWidget)

    def _switch_to_live_popup(self):
        self.centerWidget.setCurrentWidget(self.reqresWidget)
        self.liveViewWidget.setParent(None)
        self.liveViewWidget.show()

    def _switch_to_historian_popup(self):
        self.centerWidget.setCurrentWidget(self.reqresWidget)
        self.historianWidget.load(self.state_manager.db)
        self.historianWidget.setParent(None)
        self.historianWidget.show()

    def _validate_and_queue(self):

        if not self.reqWidget.stackedRequestWidget.currentWidget().validate_input(self):
            return

        message = self.reqWidget.stackedRequestWidget.currentWidget().generate_message(self.transaction_id)

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
            self.liveViewWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Disconnect')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.connected_movie)
            return
        elif message == 'DC' or message == 1000 or message == 'wstunnel_error':
            self.connected = False
            self.HomeWidget.connect_button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.resWidget.setEnabled(self.connected)
            self.liveViewWidget.setEnabled(self.connected)
            self.HomeWidget.connect_button.setText('Connect')
            self.HomeWidget.indicator.setMovie(self.HomeWidget.disconnected_movie)
            if message == 'wstunnel_error':
                ErrorDialog(self, 'Make sure WSTunnel is running!')
            elif message == 1000:
                ErrorDialog(self, 'Cannot connect to the device!')
            return
        elif message['transaction_id'] >= 128:
            print("abcd")
            self.requestLogWidget.update_log(message)
            self.responseLogWidget.update_log(message)
            if message['function_code'] <= 4:
                current_selection = getattr(Codes, self.reqWidget.dropdown.currentText().replace(' ', '_')).value
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
        else:
            self.liveViewWidget.update_view(message)

    def closeEvent(self, event):
        super(Application, self).closeEvent(event)
        self.liveViewWidget.close()
        self.historianWidget.close()
        self.state_manager.req_queue.put('DC')
        event.accept()


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
    app.exec_()
