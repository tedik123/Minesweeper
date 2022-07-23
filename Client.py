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
    def __init__(self,  username=None):
        super().__init__()

        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        # event connections
        self.client.error.connect(self.error)
        self.client.open(QUrl("ws://127.0.0.1:1302"))
        # we can use pong for the initial connection
        self.client.pong.connect(self.onPong)
        self.client.textMessageReceived.connect(lambda x: print(x))
        self.user_id = uuid.uuid1()
        if username is None:
            self.username = self.user_id
        self.username = username
        print("username:", username)


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
        self.send_object(Events.connection, {'username': self.username,
                                             'user_id': self.user_id})

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

    client = Client()

    app.exec_()
