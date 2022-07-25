from PyQt5 import QtWidgets as qtw, QtWebSockets
from PyQt5.QtCore import pyqtSignal
from requests import get

from Client import Client
from Server import MyServer


class HostDialog(qtw.QDialog):
    """Dialog for setting the settings"""
    start_game_signal = pyqtSignal(str)
    # notice this is similar to making your own custom widget/window
    # but with QDialog you get a few things for "free"
    # such as the self.accept and self.reject functions
    # and also an exec() function which tells us whether the dialog box was accepted or rejected
    def __init__(self, parent):
        # modal is whether it blocks or not, in this case it does
        super().__init__(parent, modal=True)
        # IMPORTANT
        # TODO I should not manipulate the parent within this class, rather I should send everything back after it's closed
        self.parent = parent
        self.setWindowTitle("Host Server")
        self.setLayout(qtw.QFormLayout())
        self.layout().addRow(qtw.QLabel('<h1>Server Settings</h1>'), )
        # get IP address
        # https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        # need to add port number
        ip_text = qtw.QLineEdit()
        ip_text.setText(ip)
        ip_text.setReadOnly(True)
        self.layout().addRow(qtw.QLabel("IP Addr."), ip_text)
        # now get username
        self.username_inp = qtw.QLineEdit()
        self.layout().addRow(qtw.QLabel("Username"), self.username_inp)
        self.difficulty_inp = qtw.QComboBox()
        self.difficulty_inp.addItems(["Easy", "Normal", "Hard"])
        self.layout().addRow(qtw.QLabel("Difficulty"), self.difficulty_inp)
        self.cancel_btn = qtw.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.start_btn = qtw.QPushButton("Launch")
        self.start_btn.setEnabled(False)
        # make it so they must have a username
        self.username_inp.textChanged.connect(self.enable_launch_button)
        self.start_btn.clicked.connect(self.on_launch)
        self.layout().addRow(self.cancel_btn, self.start_btn)
        # host client thing
        self.parent.client = None

    # FIXME should i really be manipulating the parent like this??
    def on_launch(self):
        print("Launching server")
        # I don't know what each one does
        # update our launch button to be our start game button instead
        self.start_btn.setText("Start Game")
        # disconnect so it doesn't overlap methods
        self.start_btn.clicked.disconnect(self.on_launch)
        self.start_btn.setDisabled(False)
        self.start_btn.clicked.connect(self.start_btn_clicked)

        # server creation
        self.parent.server_socket = QtWebSockets.QWebSocketServer('My Server',
                                                                  QtWebSockets.QWebSocketServer.NonSecureMode)
        self.parent.server = MyServer(self.parent.server_socket)

        # disable any possiblity for change
        self.username_inp.setEnabled(False)
        self.difficulty_inp.setEnabled(False)

        # create client and connect the signal to client for game launch later
        # which will occur via client requests not this dialogue
        self.parent.client = Client(self.username_inp.text(), self.parent)
        self.start_game_signal.connect(self.parent.client.request_start_game)

        # player list used for usernames
        # key is username, value is an array [label, textedit]
        self.player_widget_list = {}
        self.layout().addRow(qtw.QLabel('<h2>Player List</h2>'), )

        # set up connections
        self.parent.server.player_connected.connect(self.player_widget)
        self.parent.server.player_disconnected.connect(self.player_disconnected)
        # fill in the widget
        # self.player_widget(None, self.username_inp.text())

    # TODO player 1 should be the host!
    # this gets called on the connection and takes in the text
    def player_widget(self, user_id, username):
        player_number = len(self.player_widget_list) + 1
        player_label = qtw.QLabel(f'Player {player_number} username:')
        player_name = qtw.QLineEdit(username)
        player_name.setEnabled(False)
        self.player_widget_list[user_id] = [player_label, player_name]
        # self.player_list.append(player_name)
        self.layout().addRow(player_label, player_name)
        if len(self.player_widget_list) > 1:
            self.start_btn.setEnabled(True)

    def enable_launch_button(self, text):
        if text:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

    def on_cancel(self):
        if self.parent.server_socket:
            self.parent.server_socket.close()
            self.parent.client.close()
        # if self.parent.server:
        # do i need to delete this?
        # self.parent.server.close()
        self.close()

    # this is to delete the widgets
    def player_disconnected(self, user_id):
        player_label = self.player_widget_list[user_id][0]
        player_name = self.player_widget_list[user_id][1]
        self.layout().removeWidget(player_label)
        self.layout().removeWidget(player_name)
        player_label.deleteLater()
        player_name.deleteLater()

    def start_btn_clicked(self):
        # I need to emit everything
        # I have the player data saved to the client
        # so that leaves just difficulty?
        self.start_game_signal.emit(self.difficulty_inp.currentText())
        self.close()
