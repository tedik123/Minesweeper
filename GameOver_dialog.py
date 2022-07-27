from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtNetwork


class GameOver_dialog(qtw.QDialog):
    restart_game_signal = pyqtSignal(str)

    # player_list is to match the user_ids to the usernames
    def __init__(self, parent, winners, losers, player_data, client_user_id, isHost=False):
        # modal is whether it blocks or not, in this case it does
        super().__init__(parent, modal=True)
        self.setStyleSheet("font: Impact;"
                           "font-size: 12px;")
        self.parent = parent
        self.restart_game_signal.connect(self.parent.client.request_start_game)
        self.parent.client.start_game_signal.connect(self.close)



        self.setWindowTitle("Games Finished!")
        self.setLayout(qtw.QFormLayout())

        self.layout().addRow(qtw.QLabel('<h1>Winners</h1>'), )
        ranking = 1
        for winner_id, time in winners:
            if winner_id == client_user_id:
                current_player_label = qtw.QLabel("You" + f" \tTime: {time}")
            else:
                current_player_label = qtw.QLabel(player_data[winner_id]['username'] + f"Time: {time}")
            self.layout().addRow(str(ranking), current_player_label)
        ranking = 1
        self.layout().addRow(qtw.QLabel('<h1>Losers</h1>'), )
        for loser_id, time in losers:
            if loser_id == client_user_id:
                current_player_label = qtw.QLabel(f"\tTime: {time}")
                self.layout().addRow(str(ranking) + ". You", current_player_label)
            else:
                current_player_label = qtw.QLabel(f" \tTime: {time}")
                self.layout().addRow(str(ranking) + ". " + player_data[loser_id]['username'], current_player_label)
        self.layout().addRow(qtw.QLabel())
        self.layout().addRow(qtw.QLabel("Waiting on host for restart"),)
        if isHost:
            # todo need to finish end_game
            self.difficulty = qtw.QComboBox()
            self.difficulty.addItems(["Easy", "Normal", "Hard"])
            self.layout().addRow("Difficulty", self.difficulty)
            self.end_game_btn = qtw.QPushButton("End Games")
            self.end_game_btn.clicked.connect(self.on_cancel)
            self.play_again_btn = qtw.QPushButton("Play Again")
            self.play_again_btn.clicked.connect(self.play_again)
            self.layout().addRow(self.end_game_btn, self.play_again_btn)

    def play_again(self):
        difficulty = self.difficulty.currentText()
        self.restart_game_signal.emit(difficulty)
        self.close()

    def on_cancel(self):
        # i don't know if this is okay
        if self.parent:
            self.parent.close_socket()
            # self.parent.client.close()
        self.close()
