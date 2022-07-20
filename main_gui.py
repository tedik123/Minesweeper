import os
import sys
from Minesweeper import Minesweeper
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
# random.seed(10)

# png website

# IMPORTANT TO MAKE EXECUTABLE:  python -m auto_py_to_exe
# put this in the settings: --noconsole

class main_gui(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QGridLayout()
        self.setCentralWidget(self.main_widget)
        self.centralWidget().setLayout(self.main_layout)

        self.ms = Minesweeper()
        self.main_layout.addWidget(self.ms)
        self.show()




if __name__ == '__main__':
    # game = Minesweeper()
    # game.pretty_print_board()
    # game.game()
    path = os.getcwd()
    os.chdir(path)
    app = qtw.QApplication(sys.argv)
    app.setWindowIcon(qtg.QIcon('images/bomb_64x64.png'))
    mw = main_gui()
    # mw = Minesweeper()
    # mw.resize()

    mw.resize(400, 400)
    sys.exit(app.exec())
