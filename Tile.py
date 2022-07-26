from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import dill

class Tile(qtw.QPushButton):
    coords = qtc.pyqtSignal(int, int)
    # flagged will be used to update the flag counter in main
    # passing the coordinates since we need that for online
    flagged = qtc.pyqtSignal(bool, tuple)

    def __init__(self, row, column,value, isOnlinePlayer):
        super().__init__()
        self.MINSIZE = (32, 32)
        self.MINICONSIZE = (25, 25)
        self.setStyleSheet("margin: -1;")
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        # if not isOnlinePlayer:
        #     self.setDisabled()
        if isOnlinePlayer:
            # this basically makes it so the dummy versions are non-interactive but doesn't make it all greyed out!
            self.blockSignals(True)
        self.clicked.connect(self.coord_signal_function)

        self.row = row
        self.column = column
        self.value = value
        self.isBomb = False
        self.isVisible = False
        self.setMinimumSize(self.MINSIZE[0], self.MINSIZE[1])
        if value == "*":
            self.isBomb = True

    def set_value(self, value):
        self.value = value
        if value == "*":
            self.isBomb = True

    def get_value(self):
        return self.value

    def to_string(self):
        return str(self.value)

    def is_bomb_value(self):
        if self.isBomb:
            return 1
        return 0

    def set_isVisible(self, boolean):
        self.isVisible = boolean
        self.reveal_tile()

    # returns a string depending on if you know it's contents or not
    def show_value(self):
        if self.isVisible:
            if self.value == 0:
                return "_"
            return str(self.value)
        return "#"  # our empty non-visible symbol

    def get_pos(self):
        return self.row, self.column

    def coord_signal_function(self):
        coords = self.get_pos()
        self.coords.emit(coords[0], coords[1])

    # welp we're basically done with this function
    # just need to change it so it's appropriate to the value it actually is and if it's actually visible :shrug:
    def reveal_tile(self):
        if self.isBomb:
            icon = qtg.QIcon()
            pic = qtg.QPixmap("images/bomb_64x64.png")
            icon.addPixmap(pic, qtg.QIcon.Normal)
            icon.addPixmap(pic, qtg.QIcon.Disabled)
            self.setIcon(icon)
            # if you want to adjust icon size
            self.setIconSize(qtc.QSize(self.MINICONSIZE[0], self.MINICONSIZE[1]))

        else:
            # if it's not an empty block set the number image
            if self.value != 0:
                location = "images/numbers/" + str(self.value) + ".png"
                icon = qtg.QIcon()
                pic = qtg.QPixmap(location)
                icon.addPixmap(pic, qtg.QIcon.Normal)
                icon.addPixmap(pic, qtg.QIcon.Disabled)
                self.setIconSize(qtc.QSize(self.MINICONSIZE[0], self.MINICONSIZE[1]))
                self.setIcon(icon)
                # self.setText(self.show_value())
            else:
                self.setIcon(qtg.QIcon())
                self.setText(self.show_value())
        self.setDisabled(True)

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.RightButton:
            self.flag_button()
        else:
            super().mousePressEvent(event)

    def flag_button(self):
        if self.icon().isNull():
            self.setIcon(qtg.QIcon("images/flag2.png"))
            self.setIconSize(qtc.QSize(self.MINICONSIZE[0], self.MINICONSIZE[1]))
            self.flagged.emit(True, self.get_pos())
        else:
            self.setIcon(qtg.QIcon())
            self.flagged.emit(False, self.get_pos())


