from PySide2 import QtCore

from modbus_client.gui.style.custom_elements import *


class ConnectWidget(QWidget):

    def __init__(self, parent=None):
        super(ConnectWidget, self).__init__(parent, QtCore.Qt.Window)
        self.button = QPushButton("Connect")
        self.disconnected_movie = QtGui.QMovie("../resources/disconnected.gif")
        self.connecting_movie = QtGui.QMovie("../resources/connecting.gif")
        self.connected_movie = QtGui.QMovie("../resources/connected.gif")
        self.disconnected_movie.setScaledSize(QSize(50, 50))
        self.connecting_movie.setScaledSize(QSize(50, 50))
        self.connected_movie.setScaledSize(QSize(50, 50))
        self.indicator = QLabel()
        self.indicator.setMovie(self.disconnected_movie)
        self.disconnected_movie.start()
        self.connected_movie.start()
        self.connecting_movie.start()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.button)
        layout.addWidget(self.indicator)
        self.setLayout(layout)
