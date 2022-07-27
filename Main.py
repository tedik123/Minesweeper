import os
import sys


from GameOver_dialog import GameOver_dialog
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
        self.game_over_dialog = None
        # self.closed.connect(self.close_socket)
        # self.main_layout.addWidget(Minesweeper(True), 1, 2, 1, 1)
        # self.main_layout.addWidget(Minesweeper(True), 2, 2, 1, 1)
        # self.main_layout.addWidget(Minesweeper(True), 2, 1, 1, 1)
        self.counter = 0
        self.is_first_online = True
        self.games = {}
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
        # idk if this is necessary
        self.main_layout.setSpacing(0)
        if self.game_over_dialog:
            print("Closing game dialog")
            self.game_over_dialog.close()
            self.game_over_dialog = None
        # FIXME for now I assume only 4 players
        self.ms.set_online(True)
        self.ms.update_difficulty(difficulty)
        self.ms.resize_to_difficulty()
        # in case it was hidden by the game over screen
        # IMPORTANT I NEED TO HOOK THESE SIGNALS ONCE!!!!
        self.ms.remove_online_game_over_screen()
        # this check is to remove pairing a signal multiple times!
        if self.is_first_online:
            self.ms.board_generated_event.connect(self.client.board_generated)
            self.ms.tiles_revealed_event.connect(self.client.tiles_revealed)
            self.ms.tile_flagged_event.connect(self.client.tile_flagged)
            self.ms.game_over_event.connect(self.client.game_over)

        # we'll use this to access games, key will be UserID and value will be the game widget itself
        #    remove each one
        # to prevent overlap
        if self.games:
            for user_id, widget in self.games.items():
                widget.deleteLater()
                widget.setParent(None)
        idx = 0
        for user_id, data in self.client.player_data.items():
            print("user_id", user_id)
            print("data in start_game", data)
            current_game = Minesweeper(True)
            current_game.set_username(data['username'])
            current_game.update_difficulty(difficulty)
            current_game.resize_to_difficulty()

            if idx < 3:
                row, column, rowSpan, columnSpan = self.POSITIONS[idx]
                self.main_layout.addWidget(current_game, row, column, rowSpan, columnSpan)
            else:
                # no idea how it will position it but at least it won't break
                self.main_layout.addWidget(current_game)
            self.games[user_id] = current_game
            idx += 1

        self.client.all_games_finished_signal.connect(self.all_games_finished)
        if self.is_first_online:
            self.client.board_received_signal.connect(self.set_board)
            self.client.tiles_received_signal.connect(self.show_tiles)
            self.client.tile_flagged_signal.connect(self.tile_flagged)
            self.client.game_over_signal.connect(self.game_over)
            # for some reason if I don't disconnect it in all_games_finished method
            # it breaks and keeps spamming the dialog
            # self.client.all_games_finished_signal.connect(self.all_games_finished)

        self.is_first_online = False


    # hypothetically
    def set_board(self, content):
        user_id = content["user_id"]
        board = content["board"]
        self.games[user_id].set_board(board)

    def show_tiles(self, content):
        user_id = content["user_id"]
        tiles = content["tiles"]
        current_game = self.games[user_id]
        # have to start timer manually
        # if not current_game.timer.isActive():
        #     # tick every second
        #     current_game.timer.start(1000)
        current_game.show_tiles(tiles)

    def tile_flagged(self, content):
        user_id = content["user_id"]
        didPlaceFlag = content["didPlaceFlag"]
        coords = content["coords"]
        self.games[user_id].set_flagged(didPlaceFlag, coords)
        print("Main flagged", content)

    def game_over(self, content):
        print("CLIENT GAME OVER?????")
        user_id = content["user_id"]
        didWin = content["didWin"]
        time = content["time"]
        current_game = self.games[user_id]
        # current_game.timer.stop()
        # print("TIME STOPPED")
        current_game.online_player_game_over_screen(didWin, time)

    def all_games_finished(self, content):
        self.client.all_games_finished_signal.disconnect(self.all_games_finished)
        # check if host or not
        self.counter += 1
        print(self.counter)
        if self.server:
            print("SERVER")
            self.game_over_dialog = GameOver_dialog(self, content['winners'], content['losers'], self.client.player_data,
                                        self.client.user_id, True)
        else:
            print("CLIENT")
            self.game_over_dialog = GameOver_dialog(self, content['winners'], content['losers'], self.client.player_data,
                                        self.client.user_id, False)
        self.game_over_dialog.exec()




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
