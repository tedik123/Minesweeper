import pickle
from Events import Events
from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import QUrl
import uuid


# from TestObject import TestObject

class MyServer(QtCore.QObject):
    player_connected = QtCore.pyqtSignal([str])
    player_disconnected = QtCore.pyqtSignal(uuid.UUID, str)

    def __init__(self, parent):
        super().__init__(parent)
        # super(QtCore.QObject, self).__init__()
        self.clients = []
        self.client_data = {}
        print("server name: {}".format(parent.serverName()))
        self.server = QtWebSockets.QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        if self.server.listen(QtNetwork.QHostAddress.LocalHost, 1302):
            print('Listening: {}:{}:{}'.format(
                self.server.serverName(), self.server.serverAddress().toString(),
                str(self.server.serverPort())))
        else:
            print('error')
        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
        self.clientConnection = None
        print(self.server.isListening())
        # parent.closed.connect(app.quit)

    def onAcceptError(accept_error):
        print("Accept Error: {}".format(accept_error))

    def onNewConnection(self):
        print("onNewConnection")
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)

        self.clientConnection.textFrameReceived.connect(self.processTextFrame)

        self.clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)

        print("newClient")
        self.clients.append(self.clientConnection)
        # TODO take in a username?

    def processTextFrame(self, frame, is_last_frame):
        print("in processTextFrame")
        print("\tFrame: {} ; is_last_frame: {}".format(frame, is_last_frame))

    def processTextMessage(self, message):
        print("processTextMessage - message: {}".format(message))
        if self.clientConnection:
            for client in self.clients:
                # if client!= self.clientConnection:
                client.sendTextMessage(message)
                client.sendTextMessage("CHICKEN")

            # self.clientConnection.sendTextMessage(message)

    # def processBinaryMessage(self, message):
    #     # this is how we can translate objects back to something not cringe
    #     # important -> YAY this is how we can convert whatever data we want back to an object!
    #     # https://doc-snapshots.qt.io/qt5-5.15/echoserver.html
    #     # we want to use self.sender() to grab the client who sent it?
    #     print(self.sender())
    #     object_returned = pickle.loads(message)
    #     # print(object_returned.data)
    #     print(object_returned)
    #     print("data", object_returned.data)
    #
    #     # print("b:", pickle.loads(message))
    #     if self.clientConnection:
    #         self.clientConnection.sendBinaryMessage(message)
    #         # self.clientConnection.sendTextMessage("CRINGE")

    def processBinaryMessage(self, payload):
        # this is how we can translate objects back to something not cringe
        # important -> YAY this is how we can convert whatever data we want back to an object!
        # https://doc-snapshots.qt.io/qt5-5.15/echoserver.html
        # we want to use self.sender() to grab the client who sent it?
        client_socket = self.sender()
        object_returned = pickle.loads(payload)
        print(object_returned)
        event_type = object_returned['event']
        # FIXME this should be a switch statement but it doesn't exist in python 3.9
        if event_type == Events.connection:
            print("connection update thingy")
            self.initialConnectionInformation(client_socket, object_returned)
        else:
            print("idk haven't gotten here yet")

    # TODO this is more or less finished
    # but maybe we want to handle mid game disconnects?
    def socketDisconnected(self):
        print("socketDisconnected")
        client_socket = self.sender()
        print("client socket", client_socket)
        user_id = None
        username = None
        # key = None
        for key, data in self.client_data.items():
            if client_socket is data['socket']:
                user_id = key
                username = data["username"]
                break
        # testing if data is found
        try:
            del (self.client_data[user_id])
            self.player_disconnected.emit(user_id, username)
        # this means the connection wasn't fully formed so we have no player_data and can't be sure who disconnected?
        # besides by socket of course
        except KeyError:
            print("Connection wasn't fully formed only deleting from listed connections.")
        self.clients.remove(client_socket)
        client_socket.deleteLater()

    # this will emit a username signal back to main to update the user information and stuff
    def initialConnectionInformation(self, client_socket, payload):
        id = payload["user_id"]
        username = payload["username"]
        # we'll store all relevant data by their unique id
        self.client_data[id] = {
            'socket': client_socket,
            'username': username,
        }
        print("client list!", self.clients)
        print('client data!', self.client_data)
        self.player_connected.emit(username)


if __name__ == '__main__':
    import sys

    # why must this be defined outside of the class??!?!?!?!?!??
    parent = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.NonSecureMode)

    app = QApplication(sys.argv)
    server = MyServer(parent)

    app.exec_()
