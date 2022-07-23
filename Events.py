import enum


class Events(enum.Enum):
    connection = "connection"
    gameStart = "gameStart"
    gameEnd = "gameEnd"
    tileClicked = "tileClicked"

