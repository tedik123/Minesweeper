import math
import random
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtWidgets import QMessageBox
import os

from Tile import Tile

import json


class Minesweeper(qtw.QWidget):
    # set it to easy first!
    ROWS = 8
    COL = 10
    BOMBS = 10
    symbols = {
        'empty': "_",  # empty is the visible display
        "bomb": "*",
        'tile': "#"  # tile is hiding and not seen
    }
    DIFFICULTY = {
        #        row, column, bombs
        # 'Test': (3, 3, 0),
        'Easy': (8, 10, 10),
        'Normal': (14, 18, 40),
        'Hard': (20, 24, 99)
    }

    # SIGNAL CREATION
    # a note on this, if this causes issues when running multiple instances
    # you can subclass it to create a Qobject that contains all the signals you want, not elegant but it's a workaround
    board_generated_event = qtc.pyqtSignal(list)
    # this will be a list of tuples that will be the coordinates of the tiles revealed,
    # this of course means client side trust
    # i think that's the best way to do it, it saves having to do BFS or any other searching
    tiles_revealed_event = qtc.pyqtSignal(list)
    tile_flagged_event = qtc.pyqtSignal(bool, tuple)
    # did they win and what was their time
    game_over_event = qtc.pyqtSignal(bool, int)

    #######

    # let's say:
    # _ = empty
    # * = bomb
    # number = number
    def __init__(self, isOnlinePlayer=False):
        super().__init__()
        # is onlineplayer is basically whether to make it a dummy minesweeper game that only updates from socket calls
        self.isOnlinePlayer = isOnlinePlayer

        # this will be set on manual calls since we don't need it for non-online
        self.username = None
        # online is if it's a multiplayer game unrelated to isOnlinePlayer
        self.isOnline = False
        # self.isOnlinePlayer = isOnlinePlayer
        # self.setWindowIcon(qtg.QIcon("images/bomb_64x64.png"))
        # self.setWindowTitle("Minesweeper")
        self.board = []
        self.is_first_move = True
        self.end_game = False
        self.flag_counter = self.BOMBS
        # create the main layout
        self.main_widget = qtw.QWidget()
        self.main_layout = qtw.QVBoxLayout()
        # self.main_widget.setLayout(self.main_layout)

        self.setLayout(self.main_layout)
        # self.setCentralWidget(self.main_widget)

        # set the font stuff after the title creation
        self.create_header()
        self.create_and_set_font()
        # self.main_layout.addWidget(self.title, 1)
        self.main_layout.addWidget(self.header, 1)
        # if isOnlinePlayer:
        self.username_label = qtw.QLabel(self.username)
        self.main_layout.addWidget(self.username_label, alignment=qtc.Qt.AlignCenter)
        self.main_layout.setSpacing(0)
        # self.main_layout.setContentsMargins(-5, -5, -5, -5)
        # now the actual game layout
        self.game_widget = qtw.QWidget()
        self.grid_layout = qtw.QGridLayout()
        self.create_tiles()
        self.game_widget.setLayout(self.grid_layout)
        # self.button = qtw.QPushButton()
        self.main_layout.addWidget(self.game_widget, 5)

        self.current_difficulty = "Easy"

        if self.isOnlinePlayer:
            self.difficulty_list_widget.hide()
        # self.show()

    def create_header(self):
        # header is the whole top
        self.header = qtw.QWidget()
        self.header.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)
        self.header.setLayout(qtw.QVBoxLayout())
        self.title = qtw.QLabel("Minesweeper")
        self.header.layout().addWidget(self.title)
        self.game_info_widget = qtw.QWidget()
        # game info widget it has difficult + timer + flag count
        self.game_info_layout = qtw.QGridLayout()
        self.game_info_widget.setLayout(self.game_info_layout)
        self.game_info_layout.setSpacing(0)
        self.game_info_layout.setHorizontalSpacing(0)
        self.game_info_layout.setVerticalSpacing(0)
        self.diff_list = self.difficulty_list()
        # self.header.layout().addWidget(self.diff_list)
        self.diff_list.currentTextChanged.connect(self.update_difficulty)
        # addWidget(QWidget, int r, int c, int rowspan, int columnspan) Adds a widget at specified row and column and having specified width and/or height
        # self.game_info_layout.addWidget(self.diff_list, 1, 1, 1, 1)
        self.difficulty_list_widget = qtw.QWidget()
        self.difficulty_list_widget.setLayout(qtw.QVBoxLayout())

        self.difficulty_list_widget.layout().addWidget(self.diff_list)
        self.game_info_layout.addWidget(self.difficulty_list_widget, 1, 1, 1, 1)
        # self.timer_label = qtw.QLabel("000")
        # self.timer_label.setPicture()
        # self.timer_label.setAlignment(qtc.Qt.AlignCenter)
        # self.timer_label.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum)
        # self.game_info_layout.addWidget(self.timer_label, 1, 2, 1, 1, alignment=qtc.Qt.AlignCenter)

        self.flag_label = qtw.QLabel(f"Flag: {self.flag_counter}")

        self.game_info_layout.addWidget(self.create_timer(), 1, 2, 1, 1, alignment=qtc.Qt.AlignCenter)
        self.game_info_layout.addWidget(self.flag_label, 1, 3, 1, 1, alignment=qtc.Qt.AlignRight)
        self.header.layout().addWidget(self.game_info_widget)

    def create_timer(self):
        self.timer_widget = qtw.QWidget()
        self.timer_widget.setLayout(qtw.QHBoxLayout())
        self.timer_label = qtw.QLabel("000")
        self.timer_img = qtw.QLabel(alignment=qtc.Qt.AlignRight)
        self.timer_img.setPixmap(qtg.QPixmap("images/stopwatch.png"))
        # unfortunately you need to rescale it like this keep that in mind for the rescaling
        img_size_change = self.timer_img.pixmap().scaled(32, 32)
        self.timer_img.setPixmap(img_size_change)
        self.timer_widget.layout().addWidget(self.timer_img)
        self.timer_widget.layout().addWidget(self.timer_label)
        # self.timer is the actual timer everything else is just GUI Stuff
        self.timer = qtc.QTimer(self)
        self.seconds_count = 0
        # adding action to timer
        self.timer.timeout.connect(self.showTime)
        # update the timer every 1 second
        # self.timer.start(1000)
        return self.timer_widget

    # method called by timer
    # https://www.geeksforgeeks.org/pyqt5-digital-stopwatch/
    def showTime(self):
        self.seconds_count += 1
        # getting text from seconds_count
        text = str(self.seconds_count)
        # idk how to do a real string buffer appropriately
        # 3, cause we want like 000
        zeroes_to_add = 3 - len(text)
        zeroes_string = "0"
        if zeroes_to_add > 0:
            for i in range(zeroes_to_add):
                text = zeroes_string + text
        # showing text
        self.timer_label.setText(text)
        return

    def difficulty_list(self):
        diff_list = qtw.QComboBox()
        diff_list.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)
        for key in dict.keys(self.DIFFICULTY):
            diff_list.addItem(key)
        # you could use keys, and values to set this
        # diff_list.addItem("Easy")
        # diff_list.addItem("Normal")
        # diff_list.addItem("Hard")
        # diff_list.addItem("Test")
        return diff_list

    def update_difficulty(self, text):
        self.ROWS, self.COL, self.BOMBS = self.DIFFICULTY[text]
        self.current_difficulty = text
        self.reset_board()

    def create_tiles(self):
        self.grid_layout.setSpacing(0)
        self.grid_layout.setHorizontalSpacing(0)
        self.grid_layout.setVerticalSpacing(0)
        # this kind of works? not really?
        # self.grid_layout.setContentsMargins(-1, -1, -1, -1)
        for r in range(self.ROWS):
            current = []
            for c in range(self.COL):
                tile = Tile(r, c, self.symbols['tile'], self.isOnlinePlayer)
                # tile.clicked.connect(lambda: self.pick_spot(tile.get_pos()))
                self.grid_layout.addWidget(tile, r, c, 1, 1)
                tile.coords.connect(self.pick_spot)
                # adding the flag counter watcher
                tile.flagged.connect(self.flag_counter_update)
                current.append(tile)
                # current[-1].clicked.connect(lambda: self.pick_spot(tile.get_pos()))
            self.board.append(current)

    def reset_board(self):
        self.board = []
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.is_first_move = True
        self.create_tiles()
        self.timer_label.setText("000")
        self.seconds_count = 0
        self.flag_counter = self.BOMBS
        self.flag_label.setText(f"Flag: {self.flag_counter}")
        self.timer.stop()

    def pretty_print_board(self):
        # two spaces for the buffer
        column_headers = "  "
        for x in range(self.COL):
            column_headers += str(x) + " "
        row_headers = ""
        for x in range(self.ROWS):
            row_headers += str(x)
        print(column_headers + " |||||||| " + column_headers)
        for row in range(self.ROWS):
            string = ""
            visible_string = ""
            for column in range(self.COL):
                # string += str(self.board[row][column].to_string()) + " "
                string += self.board[row][column].show_value() + " "
                visible_string += str(self.board[row][column].get_value()) + " "
            # string += "\n"
            print(row_headers[row] + " " + string + " |||||||| " + row_headers[row] + " " + visible_string)

    def game_over_screen(self, isWon=False):
        # this one is the dummy screens; online only
        # if self.isOnlinePlayer:
        #     print("HELLO")
        #     self.online_player_game_over_screen(isWon)
        self.timer.stop()
        # this one should be the client/local version; online only
        if self.isOnline:
            print("GAME OVER BUT ONLINE")
            self.online_player_game_over_screen(isWon)
            pass
        else:
            self.msg = QMessageBox()
            self.msg.setStyleSheet("font: Impact;"
                                   "font-size: 14px;")
            self.msg.setWindowIcon(qtg.QIcon("images/bomb_64x64.png"))
            # stop the timer

            # TODO  icon if you lose and also need one if you won
            if not isWon:
                # self.msg.setIconPixmap(qtg.QPixmap("images/bomb_64x64.png"))
                self.msg.setIconPixmap(qtg.QPixmap("images/mumei_sad.png"))
                self.msg.setWindowTitle("Game Over!")
                self.msg.setText("Game Over!")
                self.msg.setInformativeText("Do you want to continue?")
            else:
                # place winner icon here
                scores = self.beat_score()
                if scores:
                    self.msg.setTextFormat(qtc.Qt.RichText)
                    self.msg.setText(f"YOU WON!<br><br>"
                                     f"You beat your high score of <b>{scores[0]}</b>!     <br>"
                                     f"Your new score is <b>{scores[0]}</b>!     "
                                     )
                else:
                    self.msg.setText("You won!")
                self.msg.setInformativeText("Do you want to continue?")
                self.msg.setIconPixmap(qtg.QPixmap("images/happy.png"))
                self.msg.setWindowTitle("You won!")
            # self.msg.setIcon()
            self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.msg.buttonClicked.connect(self.continue_game_check)
            # voodoo shit to make it run
            x = self.msg.exec_()
            # print("chic")
            return self.end_game

    def continue_game_check(self, i):
        # print(i.text())
        # print(self.windowTitle())
        if i.text() == "&Yes":
            self.end_game = False
            self.reset_board()
        else:
            self.end_game = True
            quit()

    def check_game_over(self, isGameOver=False):
        if isGameOver:
            return self.game_over_screen()
        not_shown_tiles = 0
        for row in range(self.ROWS):
            for column in range(self.COL):
                # if you're not visible add to counter
                if not self.board[row][column].isVisible:
                    not_shown_tiles += 1
        # if the only remaining tiles is equal to bombs then game is over, they won
        # print("not shown", not_shown_tiles)
        if not_shown_tiles == self.BOMBS:
            # print("You win!")
            return self.game_over_screen(True)
            # exit()
        return False

    def pick_spot(self, row, column):
        # so first move it generates everything
        # then after that is the normal generation
        # ans = input("What is your first move? (row, column)\n")
        row = int(row)
        column = int(column)
        # print(row, column)
        if self.is_first_move:
            self.first_move(row, column)
        else:
            self.search_explosion(row, column)
            # self.pretty_print_board()

    # start the timer with the first move
    def first_move(self, row, column):
        self.is_first_move = False
        self.timer.start(1000)
        self.generate_board(row, column)
        # self.pretty_print_board()

    def generate_board(self, row_given, column_given):
        restricted_spots = self.find_restricted_spots(row_given, column_given)
        for bomb in range(self.BOMBS):
            # this is terrible implementation
            # FIXME better random bomb placer plz
            while True:
                row, col = self.random_coords()
                # can't place a bomb where they chose, and in 3x3 area around it
                if row == row_given and column_given == col or (row, col) in restricted_spots:
                    pass
                # can't place a bomb on top of a bomb
                elif self.board[row][col].get_value() != self.symbols["bomb"]:
                    self.board[row][col].set_value(self.symbols["bomb"])
                    break
                # print("SFSFSFSf")

        # we have the bombs now we need to generate the numbers that are around bombs
        # then we need to generate the numbers that show bomb stuff
        self.generate_board_numbers()
        # then search explosion thing
        self.search_explosion(row_given, column_given)

    def random_coords(self):
        row = math.floor(random.random() * self.ROWS)
        col = math.floor(random.random() * self.COL)
        return row, col

    # this is bfs or dfs depending on what I decide
    def search_explosion(self, row, col):
        first_tile = self.board[row][col]
        first_tile.set_isVisible(True)
        # TODO need to handle if bomb in multiplayer
        if first_tile.isBomb:
            self.tiles_revealed_event.emit([first_tile.get_pos()])
            self.check_game_over(first_tile.isBomb)
        else:
            self.check_game_over()
        # no expansion if it's just a number, just the one
        # print(first_tile.get_value())
        if first_tile.get_value() != 0:
            self.tiles_revealed_event.emit([first_tile.get_pos()])
            return
        queue = []
        visited = []
        # will store the coords of the ones revealed, only used for online
        # not sure how to do this gracefully...
        revealed = []
        # add it to the queue and the visited
        queue.append(first_tile)
        visited.append(first_tile)
        revealed.append(first_tile.get_pos())
        while queue:
            current_tile = queue.pop(0)
            # duck me look in every direction
            row, col = current_tile.get_pos()
            # bottom left row+1, col - 1
            if not (row + 1 >= self.ROWS) and not (col - 1 < 0):
                self.search_explosion_helper(self.board[row + 1][col - 1], queue, visited, revealed)
            # left col - 1
            if not (col - 1 < 0):
                self.search_explosion_helper(self.board[row][col - 1], queue, visited, revealed)

            # top left row-1, col-1
            if not (row - 1 < 0) and not (col - 1 < 0):
                self.search_explosion_helper(self.board[row - 1][col - 1], queue, visited, revealed)

            # top
            if not (row - 1 < 0):
                self.search_explosion_helper(self.board[row - 1][col], queue, visited, revealed)

            # top right row-1, col +1
            if not (row - 1 < 0) and not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row - 1][col + 1], queue, visited, revealed)

            # right row, col +1
            if not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row][col + 1], queue, visited, revealed)

            # bottom right row+1, col+1
            if not (row + 1 >= self.ROWS) and not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row + 1][col + 1], queue, visited, revealed)

            # bottom row+1, col
            if not (row + 1 >= self.ROWS):
                self.search_explosion_helper(self.board[row + 1][col], queue, visited, revealed)
        # need to emit the revealed tiles to the client
        self.tiles_revealed_event.emit(revealed)
        self.check_game_over()

    def search_explosion_helper(self, tile, queue, visited, revealed):
        if tile not in visited:
            visited.append(tile)
            # if it's an int it's blocking and shouldn't go further
            if tile.get_value() is self.symbols['bomb']:
                return
            # only show if not a bomb
            tile.set_isVisible(True)
            revealed.append(tile.get_pos())
            if tile.get_value() > 0:
                return
            queue.append(tile)
        return

    def generate_board_numbers(self):
        for row in range(self.ROWS):
            for column in range(self.COL):
                if not self.board[row][column].isBomb:
                    self.board[row][column].set_value(self.bomb_counter_check(row, column))
            # string += "\n"
        if self.isOnline:
            self.emit_board()

    # assigns a number based on the 3x3 block range (8 blocks excluding middle) and the amount of bomb around it
    def bomb_counter_check(self, row, col):
        result = 0
        # bottom left row+1, col - 1
        if not (row + 1 >= self.ROWS) and not (col - 1 < 0):
            result += self.board[row + 1][col - 1].is_bomb_value()
        # left col - 1
        if not (col - 1 < 0):
            result += self.board[row][col - 1].is_bomb_value()

        # top left row-1, col-1
        if not (row - 1 < 0) and not (col - 1 < 0):
            result += self.board[row - 1][col - 1].is_bomb_value()

        # top
        if not (row - 1 < 0):
            result += self.board[row - 1][col].is_bomb_value()

        # top right row-1, col +1
        if not (row - 1 < 0) and not (col + 1 >= self.COL):
            result += self.board[row - 1][col + 1].is_bomb_value()

        # right row, col +1
        if not (col + 1 >= self.COL):
            result += self.board[row][col + 1].is_bomb_value()

        # bottom right row+1, col+1
        if not (row + 1 >= self.ROWS) and not (col + 1 >= self.COL):
            result += self.board[row + 1][col + 1].is_bomb_value()

        # bottom row+1, col
        if not (row + 1 >= self.ROWS):
            result += self.board[row + 1][col].is_bomb_value()

        # now set it to the empty tile if it is 0
        # if result == 0:
        #     return self.symbols['tile']
        return result

    def create_and_set_font(self):
        arcade_id = qtg.QFontDatabase.addApplicationFont('fonts/PressStart2P.ttf')
        family = qtg.QFontDatabase.applicationFontFamilies(arcade_id)[0]
        self.arcade_font = qtg.QFont(family, 8)
        self.title_font = qtg.QFont(family, 24)
        self.title.setFont(self.title_font)
        self.title.setAlignment(qtc.Qt.AlignCenter)
        self.setFont(self.arcade_font)

    def flag_counter_update(self, didPlaceFlag, coords):
        if didPlaceFlag:
            self.flag_counter -= 1
            self.flag_label.setText(f"Flag: {self.flag_counter}")
            self.tile_flagged_event.emit(didPlaceFlag, coords)
        else:
            self.flag_counter += 1
            self.flag_label.setText(f"Flag: {self.flag_counter}")
            self.tile_flagged_event.emit(didPlaceFlag, coords)

    def save_score(self):
        # load old data and append
        data = {}
        old_data = None
        # check if the score file exists
        if os.path.exists('scores.json'):
            with open('scores.json', "r") as f:
                old_data = json.load(f)
        print(data)
        if old_data:
            data = old_data
        # save it as an int
        data[self.current_difficulty] = int(self.timer_label.text())
        with open('scores.json', 'w') as f:
            json.dump(data, f)

    # definitely could've done this with a lot less file operations
    def beat_score(self):
        if os.path.exists('scores.json'):
            with open('scores.json', "r") as f:
                data = json.load(f)
                high_score = data.get(self.current_difficulty, 9999999999)
                print(high_score)
                if high_score > int(self.timer_label.text()):
                    self.save_score()
                # return old score, new score
                return (high_score, int(self.timer_label.text()))
        # they have no record save it anyway
        else:
            self.save_score()
        return False

    # TODO
    def find_restricted_spots(self, row_given, column_given):
        restricted_spots = {(row_given, column_given): ""}
        # bottom left row_given+1, column_given - 1
        if not (row_given + 1 >= self.ROWS) and not (column_given - 1 < 0):
            restricted_spots[(row_given + 1, column_given - 1)] = ""
        # left column_given - 1
        if not (column_given - 1 < 0):
            restricted_spots[(row_given, column_given - 1)] = ""
        # top left row_given-1, column_given-1
        if not (row_given - 1 < 0) and not (column_given - 1 < 0):
            restricted_spots[(row_given - 1, column_given - 1)] = ""
        # top
        if not (row_given - 1 < 0):
            restricted_spots[(row_given - 1, column_given)] = ""
        # top right row_given-1, column_given +1
        if not (row_given - 1 < 0) and not (column_given + 1 >= self.COL):
            restricted_spots[(row_given - 1, column_given + 1)] = ""
        # right row_given, column_given +1
        if not (column_given + 1 >= self.COL):
            restricted_spots[(row_given, column_given + 1)] = ""
        # bottom right row_given+1, column_given+1
        if not (row_given + 1 >= self.ROWS) and not (column_given + 1 >= self.COL):
            restricted_spots[(row_given + 1, column_given + 1)] = ""
        # bottom row_given+1, column_given
        if not (row_given + 1 >= self.ROWS):
            restricted_spots[(row_given + 1, column_given)] = ""
        return restricted_spots

    def hint_giver(self):
        probability_board = {}
        for row in range(self.ROWS):
            for column in range(self.COL):
                current_tile = self.board[row][column]
                # if it's visible add it to the probability board
                if not current_tile.isVisible:
                    probability_board[current_tile] = -1
        # now we have all tiles that are invisible
        # we need to look around in all 8 directions for 2 things
        # A) at least one must be visible
        # B) add a counter for every thing that marks it as questionable
        for tile in probability_board:
            row, col = tile.get_pos()
            neighbors = self.find_restricted_spots(row, col)
            for pos in neighbors.keys():
                n_row, n_col = pos
                neighbor_tile = self.board[n_row][n_col]

    def set_online(self, isOnline):
        if isOnline:
            self.isOnline = True
            self.set_username("You")
            self.difficulty_list_widget.hide()
        else:
            # maybe unhook signals here?
            print("Not finished")

    # this is only for online use, receives a board and sets the board to what's provided
    def set_board(self, board):
        for row in range(self.ROWS):
            for column in range(self.COL):
                self.board[row][column].set_value(board[row][column])
        # need to update this because we don't want the board to regenerate!
        self.is_first_move = False
        pass

    def emit_board(self):
        # we can't pickle the tiles directly so we need to extract the values of the generated board
        # and then send it to the server/clients
        dummy_board = []
        for row in range(self.ROWS):
            current = []
            for column in range(self.COL):
                current.append(self.board[row][column].get_value())
            dummy_board.append(current)
        self.board_generated_event.emit(dummy_board)

    # must be an array reveals the tiles given the coordinates
    def show_tiles(self, tile_coords):
        for coords in tile_coords:
            self.board[coords[0]][coords[1]].set_isVisible(True)

    def set_flagged(self, didPlaceFlag, tile_coords):
        self.board[tile_coords[0]][tile_coords[1]].flag_button()

    # emits the signal of game over to server
    # and displays locally game over
    def online_player_game_over_screen(self, isWon, time= None):
        self.game_widget.hide()
        self.game_over_pic = qtw.QLabel()
        self.game_over_container = qtw.QWidget()
        # self.container.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)
        self.game_over_layout = qtw.QGridLayout()
        title_string = ""
        self.game_over_container.setLayout(self.game_over_layout)
        if not time:
            time = self.timer_label.text()
        # Emit game data for client use
        self.game_over_event.emit(isWon, int(time))
        if isWon:
            title_string = "You Won!"
            self.game_over_pic.setPixmap(qtg.QPixmap("images/happy.png").scaled(133, 160))


        else:
            title_string = "You Lost!"
            self.game_over_pic.setPixmap(qtg.QPixmap("images/mumei_sad.png"))

        self.game_over_info = qtw.QWidget()
        self.game_over_info.setLayout(qtw.QVBoxLayout())
        self.main_layout.addWidget(self.game_over_container)
        self.game_over_layout.addWidget(self.game_over_pic, 1, 1)
        self.game_over_layout.addWidget(self.game_over_info, 1, 2)
        # self.game_over_layout.addWidget(qtw.QLabel("TITLE"), 1, 2, 1, 1)
        # self.game_over_layout.addWidget(qtw.QLabel("Timer "), 2, 2, 1, 1)
        # self.game_over_layout.addWidget(qtw.QLabel("Waiting for players"), 3, 2, 1, 1)
        self.game_over_info.layout().addWidget(qtw.QLabel(f'<h1>{title_string}<h1>'))
        self.game_over_info.layout().addWidget(qtw.QLabel(f"Timer: {time} sec(s)"))
        waiting_label = qtw.QLabel("Waiting for other players")
        waiting_label.setWordWrap(True)
        self.game_over_info.layout().addWidget(waiting_label)
        # self.game_over_layout.layout().setVerticalSpacing(0)
        # self.game_over_layout.addStretch()
        self.main_layout.addStretch()

    def remove_online_game_over_screen(self):
        try:
            self.game_over_container.hide()
            self.game_widget.show()
        except AttributeError:
            print("Nothing to hide.")

    def set_username(self, name):
        self.username = name
        self.username_label.setText(name)