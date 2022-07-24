import pickle
import sys

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication
from TestObject import TestObject
from Events import Events

# we'll use this as a unique identifier, passed along with the username
import uuid


# https://stackoverflow.com/questions/35237245/how-to-create-a-websocket-client-by-using-qwebsocket-in-pyqt5
class Client(QtCore.QObject):
    # IMPORTANT so for someone to connect they must use the public ip + port
    #  for the host that means they need to have that port forwarded unfortunately!
    #  also if it's the host they need to connect via ipv4 not ipv6!
    def __init__(self,  username, parent=None):
        super().__init__()
        if parent is not None:
            parent.start_game_signal.connect(self.start_game)

        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        # event connections
        self.client.error.connect(self.error)
        # self.client.open(QUrl("ws://127.0.0.1:1302"))
        self.client.open(QUrl("ws://127.0.0.1:7777"))

        # self.client.open(QUrl("ws://127.0.0.1:25565"))
        # THIS is the format for public IPs!
        # self.client.open(QUrl("ws://174.16.75.62:7777"))
        # 25565 - minecraft port which i have open
        # we can use pong for the initial connection
        self.client.pong.connect(self.onPong)
        self.client.textMessageReceived.connect(lambda x: print(x))
        self.client.binaryMessageReceived.connect(self.on_binary_message)
        self.user_id = uuid.uuid1()
        if username is None:
            self.username = self.user_id
        self.username = username
        print("username:", username)
        # contains other player data NOT including this client
        self.player_data = {}


    def do_ping(self):
        print("client: do_ping")
        self.client.ping(b"foo")

    def send_message(self):
        print("client: send_message")
        self.client.sendTextMessage("asd")
        # someobject = {"chicken": "dinner"}
        # someobject = TestObject()
        # print(someobject)
        # print(someobject.data)
        # someobject_bytes = pickle.dumps(someobject)
        # self.client.sendBinaryMessage(someobject_bytes)

    # used for the initial connection set up
    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))
        self.send_object(Events.Connection, {'username': self.username,
                                             'user_id': self.user_id})


    def on_binary_message(self, payload):
        try:
            content = pickle.loads(payload)
            print(content)
            event_type = content['event']
        except KeyError:
            return print("No event type provided! Ignoring!")

        #   rest of code
        if event_type == Events.Connection:
            self.connection_information(content)
        elif event_type == Events.Disconnect:
            self.on_disconnect(content)
        elif event_type == Events.GameStart:
            self.on_game_start(content)
        else:
            print("Not created yet.")


    def connection_information(self, content):
        for key, data in content.items():
            # kinda slow but eh
            if key != 'event' and key != self.user_id and key not in self.player_data:
                self.player_data[key] = data

        print("Player connections:\n", self.player_data)



    # TODO handle GUI changes as well here with signals...but that's last
    # this just receives an event type and a dict formatted as "user_id": user_id
    def on_disconnect(self, content):
        for key, user_id in content.items():
            # probs do something else too
            if key != 'event':
                del(self.player_data[user_id])
                print("Deleted")
                print(self.player_data)


    # so here the client needs to emit to main how many games to create?
    # and then we need to tie the userIds to the game as well as display their usernames as headers?
    def on_game_start(self, content):
        print("Game start content", content)

    def request_start_game(self, difficulty):
        self.send_object(Events.GameStart, {'difficulty': difficulty})




    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def close(self):
        self.client.close()


    # we can just send a dict and the key will be the event name
    # the dict will be formatted very similarly to a json
    # content must be formatted as a dictionary!
    def send_object(self, key, content):
        header = {"event": key}
        # this basically zips the dictionaries together by piping one into the other
        content_to_send = header | content
        # serialize it
        content_bytes = pickle.dumps(content_to_send)
        # send
        self.client.sendBinaryMessage(content_bytes)


# these are for testing!
def quit_app():
    print("timer timeout - exiting")
    QCoreApplication.quit()


def ping():
    client.do_ping()


def send_message():
    client.send_message()


if __name__ == '__main__':
    global client
    app = QApplication(sys.argv)

    QTimer.singleShot(2000, ping)
    QTimer.singleShot(3000, send_message)
    # QTimer.singleShot(5000, quit_app)

    client = Client("Mr. Chiken")
    app.aboutToQuit.connect(client.close)
    app.exec_()
