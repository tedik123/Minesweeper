import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# font
# libsans_id = qtg.QFontDatabase.addApplicationFont(':/fonts/LiberationSans-Regular.ttf')
# print(libsans_id)
# # we can then use the ID number to find the font's family string
# family = qtg.QFontDatabase.applicationFontFamilies(libsans_id)[0]
# print(family)
# libsans = qtg.QFont(family, 10)
# # inputs['Team'].setFont(libsans)


class MainWindow(qtw.QMainWindow):
    # you can use this to readjust the icon size based on some wacky ass formula you come up with
    # just connect it to each button
    resized = qtc.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.create_and_set_font()
        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QVBoxLayout()

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        self.title = qtw.QLabel("Minesweeper")
        self.main_layout.addWidget(self.title, 1)
        self.game_widget = qtw.QWidget()
        self.grid_layout = qtw.QGridLayout()
        # self.grid_layout.addWidget(qtw.QPushButton(), 1, 1, 1, 1)
        # self.grid_layout.addWidget(qtw.QPushButton(), 4, 1, 1, 1)
        self.create_buttons(9, 9)
        self.game_widget.setLayout(self.grid_layout)
        # self.button = qtw.QPushButton()
        self.main_layout.addWidget(self.game_widget, 5)
        self.show()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        print("Reized")

    def create_buttons(self, row, col):
        self.grid_layout.setSpacing(0)
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)
        # this kind of works? not really?
        # self.grid_layout.setContentsMargins(-1, -1, -1, -1)

        for r in range(row):
            for c in range(col):
                button = Buttons()
                # button = qtw.QPushButton()
                # button.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
                # background-image : url(images/bomb_64x64.png);
                # this makes it a bomb
                # button.clicked.connect(lambda: button.setIcon(qtg.QIcon("images/bomb_64x64.png")))
                # button.setIcon(qtg.QIcon("images/bomb_64x64.png"))
                self.grid_layout.addWidget(button, r, c, 1, 1)

    # def change_icon(self):
    def create_and_set_font(self):
        arcade_id = qtg.QFontDatabase.addApplicationFont('fonts/PressStart2P.ttf')
        family = qtg.QFontDatabase.applicationFontFamilies(arcade_id)[0]
        arcade_font = qtg.QFont(family, 10)
        self.setFont(arcade_font)


class Buttons(qtw.QPushButton):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("margin: -1; ")
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.clicked.connect(self.change_icon)

    # welp we're basically done with this function
    # just need to change it so it's appropriate to the value it actually is and if it's actually visible :shrug:
    def change_icon(self):
        self.setIcon(qtg.QIcon("images/bomb_64x64.png"))
        # if you want to adjust icon size
        self.setIconSize(qtc.QSize(25, 25))

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.resize(400, 400)
    sys.exit(app.exec())
