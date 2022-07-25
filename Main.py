import os
import sys

import dill

from Minesweeper import Minesweeper
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

from Tile import Tile
from host_dialog import HostDialog
from ConnectDialog import ConnectDialog


# random.seed(10)

# png website

# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe
# put this in the settings: --noconsole


# main here can just hanlde the server creation as well as client creations
# each client passed back from the server will be used to pass in a socket
# that way

# we need to create the socket in main here and pass it back to minesweeper
# or simply create signals for the minesweeper game
# connect it to the socket


class Main(qtw.QMainWindow):
    # for 3 other players at most to position them correctly
    POSITIONS = [[1, 2, 1, 1],
                 [2, 2, 1, 1],
                 [2, 1, 1, 1]]

    def __init__(self):
        super().__init__()
        self.setWindowIcon(qtg.QIcon("images/bomb_64x64.png"))
        self.setWindowTitle("Minesweeper")
        self.server_socket = None
        self.server = None
        self.client = None
        self.create_toolbar()
        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QGridLayout()
        self.setCentralWidget(self.main_widget)
        self.centralWidget().setLayout(self.main_layout)
        self.ms = Minesweeper()
        self.main_layout.addWidget(self.ms, 1, 1, 1, 1)
        # self.closed.connect(self.close_socket)
        # self.main_layout.addWidget(Minesweeper(True), 1, 2, 1, 1)
        # self.main_layout.addWidget(Minesweeper(True), 2, 2, 1, 1)
        # self.main_layout.addWidget(Minesweeper(True), 2, 1, 1, 1)
        self.show()

    def create_toolbar(self):
        self.toolbar = self.addToolBar('Online')
        self.toolbar.addAction('Host', self.host)
        self.toolbar.addAction('Connect', self.connect_to_server)

    # this will create the server and the client for the host
    def host(self):
        host_dialog = HostDialog(self)
        host_dialog.exec()

    def connect_to_server(self):
        connect_dialog = ConnectDialog(self)
        connect_dialog.exec()

    def close_socket(self):
        if self.server_socket:
            self.server_socket.close()

    # receives a signal providing the difficulty
    def start_game(self, difficulty):
        # FIXME for now I assume only 4 players
        self.ms.set_online(True)
        self.ms.update_difficulty(difficulty)
        self.ms.board_generated_event.connect(self.client.board_generated)
        self.ms.tiles_revealed_event.connect(self.client.tiles_revealed)

        # we'll use this to access games, key will be UserID and value will be the game widget itself
        self.games: dict[Minesweeper] = {}
        idx = 0
        for user_id, data in self.client.player_data.items():
            print("user_id", user_id)
            print("data in start_game", data)
            current_game = Minesweeper(True)
            if idx < 3:
                row, column, rowSpan, columnSpan = self.POSITIONS[idx]
                self.main_layout.addWidget(current_game, row, column, rowSpan, columnSpan)
            else:
                # no idea how it will position it but at least it won't break
                self.main_layout.addWidget(current_game)
            self.games[user_id] = current_game
            idx+=1

        self.client.board_received_signal.connect(self.set_board)
        self.client.tiles_received_signal.connect(self.show_tiles)

        # TODO add the other players for now I just want to do one and send the signals back to server and other clients

    # hypothetically
    def set_board(self, content):
        user_id = content["user_id"]
        board = content["board"]
        self.games[user_id].set_board(board)

    def show_tiles(self, content):
        user_id = content["user_id"]
        tiles = content["tiles"]
        self.games[user_id].show_tiles(tiles)

#    on game over you can just disable the parent widget! https://stackoverflow.com/questions/34888407/how-to-disable-widgets-that-belong-to-layout-in-qt
# maybe of course lol

if __name__ == '__main__':
    # game = Minesweeper()
    # game.pretty_print_board()
    # game.game()
    path = os.getcwd()
    os.chdir(path)
    app = qtw.QApplication(sys.argv)
    app.setWindowIcon(qtg.QIcon('images/bomb_64x64.png'))
    mw = Main()

    app.aboutToQuit.connect(mw.close_socket)

    # mw = Minesweeper()
    # mw.resize()

    mw.resize(400, 400)
    sys.exit(app.exec())
