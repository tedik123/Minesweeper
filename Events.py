import enum


class Events(enum.Enum):
    Connection = "connection"
    Disconnect = "disconnect"
    GameStart = "gameStart"
    GameEnd = "gameEnd"
    TilesRevealed = "TilesRevealed"
    BoardGenerated= "BoardGenerated"

