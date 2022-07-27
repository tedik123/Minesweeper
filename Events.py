import enum


class Events(enum.Enum):
    Connection = "connection"
    Disconnect = "disconnect"
    GameStart = "gameStart"
    GameOver = "gameOver"
    AllFinished = "AllFinished"
    TilesRevealed = "TilesRevealed"
    BoardGenerated = "BoardGenerated"
    TileFlagged = "TileFlagged"

