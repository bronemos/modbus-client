from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets import *
from modbus_client.gui.widgets import RequestWidget


class Application(QMainWindow):
    connected = False

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

        self.resWidget = ResponseWidget()
        self.resWidget.setEnabled(self.connected)

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
        self.historianWidget.export_request_history.clicked.connect(
            lambda: self.state_manager.user_req_queue.put('export_request'))
        self.historianWidget.export_response_history.clicked.connect(
            lambda: self.state_manager.user_req_queue.put('export_response'))
        self.liveViewWidget = LiveViewWidget(self.state_manager.user_req_queue)
        self.state_manager.update_counter.connect(self.liveViewWidget.progressBar.setValue)
        self.state_manager.initiate_live_view_update.connect(self.liveViewWidget.update_view_request)
        self.state_manager.update_view.connect(self.liveViewWidget.update_view)
        self.state_manager.update_historian.connect(self.historianWidget.load)
        self.state_manager.export_response.connect(self.historianWidget.export_response_history_to_csv)
        self.state_manager.export_request.connect(self.historianWidget.export_response_history_to_csv)
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
            self.state_manager.user_req_queue.put('CONN')
        else:
            self.state_manager.user_req_queue.put('DC')
            self.update_gui('DC')

    def _switch_to_historian(self):
        if self.centerWidget.currentWidget() != self.historianWidget:
            self.state_manager.user_req_queue.put('update_historian')
            self.centerWidget.addWidget(self.historianWidget)
            self.centerWidget.setCurrentWidget(self.historianWidget)
            self.HomeWidget.live_button.setChecked(False)
        else:
            self.centerWidget.setCurrentWidget(self.reqresWidget)
            self.HomeWidget.live_button.setChecked(False)

    def _switch_to_live(self):
        if self.centerWidget.currentWidget() != self.liveViewWidget:
            self.centerWidget.addWidget(self.liveViewWidget)
            self.centerWidget.setCurrentWidget(self.liveViewWidget)
            self.HomeWidget.historian_button.setChecked(False)
        else:
            self.centerWidget.setCurrentWidget(self.reqresWidget)
            self.HomeWidget.historian_button.setChecked(False)

    def _switch_to_live_popup(self):
        if self.centerWidget.currentWidget() == self.liveViewWidget:
            self.centerWidget.setCurrentWidget(self.reqresWidget)
            self.HomeWidget.live_button.setChecked(False)
        self.liveViewWidget.setParent(None)
        self.liveViewWidget.show()
        self.liveViewWidget.ReadCoilsResponse.setFocus()

    def _switch_to_historian_popup(self):
        if self.centerWidget.currentWidget() == self.historianWidget:
            self.centerWidget.setCurrentWidget(self.reqresWidget)
            self.HomeWidget.historian_button.setChecked(False)
        self.state_manager.user_req_queue.put('update_historian')
        self.historianWidget.setParent(None)
        self.historianWidget.show()

    def _validate_and_queue(self):

        if not self.reqWidget.stackedRequestWidget.currentWidget().validate_input(self):
            return

        message = self.reqWidget.stackedRequestWidget.currentWidget().generate_message()

        message['user_generated'] = True

        self.state_manager.user_req_queue.put(message)

    def update_gui(self, message):
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
        else:
            self.requestLogWidget.update_log(message)
            self.responseLogWidget.update_log(message)
            self.resWidget.update_response(message)

    def closeEvent(self, event):
        super(Application, self).closeEvent(event)
        self.liveViewWidget.close()
        self.historianWidget.close()
        self.state_manager.user_req_queue.put('DC')
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
