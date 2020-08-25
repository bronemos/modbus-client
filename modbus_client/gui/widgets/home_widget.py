import os

from PySide2 import QtCore

from modbus_client.gui.style.custom_elements import *


class HomeWidget(QWidget):

    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent, QtCore.Qt.Window)
        self.connect_button = QPushButton('Connect')
        self.historian_button = QPushButton('Historian')
        self.historian_button.setCheckable(True)
        self.live_button = QPushButton('Live View')
        self.live_button.setCheckable(True)
        path = os.path.abspath(__file__ + '/../../../resources')
        self.disconnected_movie = QtGui.QMovie(path + '/disconnected.gif')
        self.connecting_movie = QtGui.QMovie(path + '/connecting.gif')
        self.connected_movie = QtGui.QMovie(path + '/connected.gif')
        self.disconnected_movie.setScaledSize(QSize(50, 50))
        self.connecting_movie.setScaledSize(QSize(50, 50))
        self.connected_movie.setScaledSize(QSize(50, 50))
        self.indicator = QLabel()
        self.indicator.setAlignment(Qt.AlignCenter)
        self.indicator.setMovie(self.disconnected_movie)
        self.disconnected_movie.start()
        self.connected_movie.start()
        self.connecting_movie.start()

        self.live_popup = QPushButton()
        live_pixmap = QPixmap(path + '/popup.png')
        self.live_popup.setIcon(live_pixmap)
        self.live_popup.resize(live_pixmap.rect().size())
        live_layout = QHBoxLayout()
        live_layout.addWidget(self.live_button)
        live_layout.addWidget(self.live_popup)

        self.historian_popup = QPushButton()
        historian_pixmap = QPixmap(path + '/popup.png')
        self.historian_popup.setIcon(historian_pixmap)
        self.historian_popup.resize(historian_pixmap.rect().size())
        historian_layout = QHBoxLayout()
        historian_layout.addWidget(self.historian_button)
        historian_layout.addWidget(self.historian_popup)

        connect_layout = QVBoxLayout()
        connect_layout.setAlignment(Qt.AlignCenter)
        connect_layout.addLayout(historian_layout)
        connect_layout.addLayout(live_layout)
        connect_layout.addWidget(self.connect_button)
        connect_layout.addWidget(self.indicator)

        connect_widget = QWidget()
        connect_widget.setLayout(connect_layout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(connect_widget)
        self.setLayout(layout)
