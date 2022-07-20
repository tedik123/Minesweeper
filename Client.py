import pickle
import sys

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication
from TestObject import TestObject


# https://stackoverflow.com/questions/35237245/how-to-create-a-websocket-client-by-using-qwebsocket-in-pyqt5
class Client(QtCore.QObject):
    def __init__(self, parent):
        super().__init__()

        self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        # event connections
        self.client.error.connect(self.error)
        self.client.open(QUrl("ws://127.0.0.1:1302"))
        self.client.pong.connect(self.onPong)
        self.client.textMessageReceived.connect(lambda x: print(x))

    def do_ping(self):
        print("client: do_ping")
        self.client.ping(b"foo")

    def send_message(self):
        print("client: send_message")
        self.client.sendTextMessage("asd")
        # someobject = {"chicken": "dinner"}
        someobject = TestObject()
        print(someobject)
        print(someobject.data)
        someobject_bytes = pickle.dumps(someobject)
        self.client.sendBinaryMessage(someobject_bytes)

    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def close(self):
        self.client.close()

    # we can just send a dict and the key will be the event name
    def send_object(self,key,content):
        content_bytes = pickle.dumps(content)
        # need key here before sending
        self.client.sendBinaryMessage([key, content_bytes])


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
    QTimer.singleShot(5000, quit_app)

    client = Client(app)

    app.exec_()
