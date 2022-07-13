import pickle

from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import QUrl
from TestObject import TestObject

class MyServer(QtCore.QObject):

    def __init__(self, parent):
        super().__init__(parent)
        # super(QtCore.QObject, self).__init__()
        self.clients = []
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
        parent.closed.connect(app.quit)

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

    def processBinaryMessage(self, message):
        # this is how we can translate objects back to something not cringe
        # important -> YAY this is how we can convert whatever data we want back to an object!
        object_returned = pickle.loads(message)
        print(object_returned.data)
        # print("b:", pickle.loads(message))
        if self.clientConnection:
            self.clientConnection.sendBinaryMessage(message)
            # self.clientConnection.sendTextMessage("CRINGE")

    def socketDisconnected(self):
        print("socketDisconnected")
        if self.clientConnection:
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()




if __name__ == '__main__':
    import sys
    # why must this be defined outside of the class??!?!?!?!?!??
    parent = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.NonSecureMode)

    app = QApplication(sys.argv)
    server = MyServer(parent)

    app.exec_()
