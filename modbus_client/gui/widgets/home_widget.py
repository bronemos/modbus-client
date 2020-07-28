from PySide2 import QtCore

from modbus_client.gui.style.custom_elements import *


class HomeWidget(QWidget):

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent, QtCore.Qt.Window)
        self.connect_button = QPushButton("Connect")
        self.historian_button = QPushButton(" " * 6 + "Historian" + " " * 6)
        self.disconnected_movie = QtGui.QMovie("../modbus_client/resources/disconnected.gif")
        self.connecting_movie = QtGui.QMovie("../modbus_client/resources/connecting.gif")
        self.connected_movie = QtGui.QMovie("../modbus_client/resources/connected.gif")
        self.disconnected_movie.setScaledSize(QSize(50, 50))
        self.connecting_movie.setScaledSize(QSize(50, 50))
        self.connected_movie.setScaledSize(QSize(50, 50))
        self.indicator = QLabel()
        self.indicator.setAlignment(Qt.AlignCenter)
        self.indicator.setMovie(self.disconnected_movie)
        self.disconnected_movie.start()
        self.connected_movie.start()
        self.connecting_movie.start()

        connect_layout = QVBoxLayout()
        connect_layout.setAlignment(Qt.AlignCenter)
        connect_layout.addWidget(self.historian_button)
        connect_layout.addWidget(QHLine())
        connect_layout.addWidget(self.connect_button)
        connect_layout.addWidget(self.indicator)

        connect_widget = QWidget()
        connect_widget.setLayout(connect_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        # layout.addWidget(QPushButton("HISTORIAN"))
        layout.addWidget(connect_widget)
        self.setLayout(layout)
