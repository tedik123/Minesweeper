import os
import sys
from Minesweeper import Minesweeper
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from host_dialog import HostDialog

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


class main_gui(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(qtg.QIcon("images/bomb_64x64.png"))
        self.setWindowTitle("Minesweeper")
        self.server_socket = None
        self.server = None
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

    def host(self):
        host_dialog = HostDialog(self)
        host_dialog.exec()

    def connect_to_server(self):
        pass

    def close_socket(self):
        if self.server_socket:
            self.server_socket.close()



if __name__ == '__main__':
    # game = Minesweeper()
    # game.pretty_print_board()
    # game.game()
    path = os.getcwd()
    os.chdir(path)
    app = qtw.QApplication(sys.argv)
    app.setWindowIcon(qtg.QIcon('images/bomb_64x64.png'))
    mw = main_gui()
    app.aboutToQuit.connect(mw.close_socket)

    # mw = Minesweeper()
    # mw.resize()

    mw.resize(400, 400)
    sys.exit(app.exec())
