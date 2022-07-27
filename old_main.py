import math
import random
random.seed(10)


class Minesweeper:
    COL = 10
    ROWS = 8
    BOMBS = 10
    symbols = {
        'empty': "_", #empty is the visible display
        "bomb": "*",
        'tile' : "#" #tile is hiding and not seen
    }

    # let's say:
    # _ = empty
    # * = bomb
    # number = number
    def __init__(self):
        self.board = []
        self.is_first_move = True
        for row in range(self.ROWS):
            current = []
            for column in range(self.COL):
                current.append(Tile(row, column, self.symbols['tile']))
            self.board.append(current)
        # print(self.board)

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

    def game(self):
        isGameOver = False
        while not isGameOver:
            game.pick_spot()
            isGameOver = self.check_game_over()

    def check_game_over(self):
        not_shown_tiles = 0
        for row in range(self.ROWS):
            for column in range(self.COL):
                # if you're not visible add to counter
                if not self.board[row][column].isVisible:
                    not_shown_tiles+=1
        # if the only remaining tiles is equal to bombs then game is over, they won
        if not_shown_tiles == self.BOMBS:
            print("You win!")
            exit()
        return False

    def pick_spot(self):
        # so first move it generates everything
        # then after that is the normal generation
        ans = input("What is your first move? (row, column)\n")
        row, column = ans.split()
        row = int(row)
        column = int(column)
        print(row, column)
        if self.is_first_move:
            self.first_move(row, column)
        else:
            self.search_explosion(row, column)
            self.pretty_print_board()


    def first_move(self, row, column):
        self.is_first_move = False
        self.generate_board(row, column)
        self.pretty_print_board()

    def generate_board(self, row_given, column_given):
        for bomb in range(self.BOMBS):
            # this is terrible implementation
            # FIXME better random bomb placer plz
            while True:
                row, col = self.random_coords()
                # can't place a bomb where they chose
                if row == row_given and column_given == col:
                    pass
                # can't place a bomb on top of a bomb
                elif self.board[row][col].get_value() != self.symbols["bomb"]:
                    self.board[row][col].set_value(self.symbols["bomb"])
                    break

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
        if first_tile.isBomb:
            print("Game Over")
            exit()
        # no expansion if it's just a number, just the one
        print(first_tile.get_value())
        if first_tile.get_value() != 0:
            return
        queue = []
        visited = []
        # add it to the queue and the visited
        queue.append(first_tile)
        visited.append(first_tile)
        while queue:
            current_tile = queue.pop(0)
            # duck me look in every direction
            row, col = current_tile.get_pos()
            # bottom left row+1, col - 1
            if not (row + 1 >= self.ROWS) and not (col - 1 < 0):
                self.search_explosion_helper(self.board[row + 1][col - 1], queue, visited)
            # left col - 1
            if not (col - 1 < 0):
                self.search_explosion_helper(self.board[row][col - 1], queue, visited)

            # top left row-1, col-1
            if not (row - 1 < 0) and not (col - 1 < 0):
                self.search_explosion_helper(self.board[row - 1][col - 1], queue, visited)

            # top
            if not (row - 1 < 0):
                self.search_explosion_helper(self.board[row - 1][col], queue, visited)

            # top right row-1, col +1
            if not (row - 1 < 0) and not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row - 1][col + 1], queue, visited)

            # right row, col +1
            if not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row][col + 1], queue, visited)

            # bottom right row+1, col+1
            if not (row + 1 >= self.ROWS) and not (col + 1 >= self.COL):
                self.search_explosion_helper(self.board[row + 1][col + 1], queue, visited)

            # bottom row+1, col
            if not (row + 1 >= self.ROWS):
                self.search_explosion_helper(self.board[row + 1][col], queue, visited)


    def search_explosion_helper(self, tile, queue, visited):
        if tile not in visited:
            visited.append(tile)
            # if it's an int it's blocking and shouldn't go further
            if tile.get_value() is self.symbols['bomb']:
                return
            # only show if not a bomb
            tile.set_isVisible(True)
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

    # assigns a number based on the 8 block range and the amount of bomb around it
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


class Tile:

    def __init__(self, row, column, value=None):
        self.row = row
        self.column = column
        self.value = value
        self.isBomb = False
        self.isVisible = False
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

    # returns a string depending on if you know it's contents or not
    def show_value(self):
        if self.isVisible:
            if self.value == 0:
                return "_"
            return str(self.value)
        return "#"  # our empty non-visible symbol

    def get_pos(self):
        return self.row, self.column


if __name__ == '__main__':
    game = Minesweeper()
    game.pretty_print_board()
    game.game()


