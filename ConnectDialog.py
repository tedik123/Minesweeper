from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtNetwork
from requests import get

from Client import Client


class ConnectDialog(qtw.QDialog):
    """Dialog for setting the settings"""
    start_game_signal = pyqtSignal(str)
    # notice this is similar to making your own custom widget/window
    # but with QDialog you get a few things for "free"
    # such as the self.accept and self.reject functions
    # and also an exec() function which tells us whether the dialog box was accepted or rejected
    def __init__(self, parent):
        # modal is whether it blocks or not, in this case it does
        super().__init__(parent, modal=True)

        self.parent = parent
        self.setWindowTitle("Connect to Host")
        self.setLayout(qtw.QFormLayout())
        self.layout().addRow(qtw.QLabel('<h1>Server Settings</h1>'), )
        # need to add port number
        self.ip_text = qtw.QLineEdit()
        self.ip_text.setPlaceholderText("192.169.0.1")
        self.ip_text.textChanged.connect(self.enable_connect_button)
        # ip_text.setReadOnly(True)
        self.layout().addRow(qtw.QLabel("Host IP Addr."), self.ip_text)
        self.port_num_text = qtw.QLineEdit()
        self.port_num_text.setText("7777")
        self.layout().addRow(qtw.QLabel("Port"), self.port_num_text)
        # now get username
        self.username_inp = qtw.QLineEdit()
        self.layout().addRow(qtw.QLabel("Username"), self.username_inp)

        self.cancel_btn = qtw.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.connect_btn = qtw.QPushButton("Launch")
        self.connect_btn.setEnabled(False)
        # make it so they must have a username
        self.username_inp.textChanged.connect(self.enable_connect_button)
        self.connect_btn.clicked.connect(self.on_launch)
        self.layout().addRow(self.cancel_btn, self.connect_btn)
        # host client thing
        self.parent.client = None


    def enable_connect_button(self):
        addr = QtNetwork.QHostAddress()
        if addr.setAddress(self.ip_text.text()) and self.username_inp.text():
            # valid
            self.connect_btn.setEnabled(True)
        # else:
        #     # invalid
        #     pass

    def on_cancel(self):
        # i don't know if this is okay
        if self.parent.client:
            self.parent.client.deleteLater()
            # self.parent.client.close()
        self.close()


    def on_launch(self):
        # self.setLayout(qtw.QHBoxLayout())
        self.info_label = qtw.QLabel("Connecting to host...", )
        self.layout().addWidget(self.info_label)
        self.parent.client = Client(self.username_inp.text(), self.parent)
        self.parent.client.successful_connection.connect(self.change_status)

    def change_status(self, successful):
        if successful:
            self.info_label.setText("Connection successful, waiting on host.")
            self.connect_btn.setDisabled(True)
            # this waits for the game to start before closing itself, start game is handled in parent
            self.parent.client.start_game_signal.connect(self.close)
        else:
            self.info_label.setText("Connection failed!")

    # def start_game_received(self):
    #     self.parent.client.start_game_signal.connect(self.parent.start_game)
    #     self.close()