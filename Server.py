import pickle
from Events import Events
from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import QUrl
import uuid


# from TestObject import TestObject

class MyServer(QtCore.QObject):
    player_connected = QtCore.pyqtSignal(uuid.UUID, str)
    player_disconnected = QtCore.pyqtSignal(uuid.UUID, str)
    all_players_finished = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        # super(QtCore.QObject, self).__init__()
        self.clients = []
        self.client_data = {}
        # used to see how many games have finished
        self.game_counter = 0
        self.winners = {}
        self.losers = {}

        print("server name: {}".format(parent.serverName()))
        self.server = QtWebSockets.QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        # "ws://174.16.75.62:25565"
        # print(QtNetwork.QHostAddress.))
        # if self.server.listen(QtNetwork.QHostAddress.LocalHost, 1302):
        # # from here to the if statement is absolutely useless code!
        # host_adr = QtNetwork.QHostAddress("174.16.75.62")
        # print(host_adr.toIPv6Address())
        # # public_adr = host_adr.toIPv6Address()
        # # if self.server.listen(QtNetwork.QHostAddress.LocalHost, 1302):
        # host = host_adr.setAddress("174.16.75.62")
        # # addr = QtNetwork.QHostAddress.Any
        # addr = '.'.join(str(x) for x in host_adr.toIPv6Address()[-4:])
        # print(f'Public ip address: {addr}')

        # any basically means that it'll look to Ipv6 and Ipv4 addresses as long as it's the right port!
        if self.server.listen(QtNetwork.QHostAddress.Any, 7777):
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
        print("New client connecting...")
        clientConnection = self.server.nextPendingConnection()
        clientConnection.textMessageReceived.connect(self.processTextMessage)

        clientConnection.textFrameReceived.connect(self.processTextFrame)

        clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        clientConnection.disconnected.connect(self.socketDisconnected)

        print("New Client added to list.")
        # FIXME I'm worried that if a player connects and doesn't send their username then it'll cause issues...?
        # should I append or wait until it's on the initial connection information?
        self.clients.append(clientConnection)

    def processTextFrame(self, frame, is_last_frame):
        # print("in processTextFrame")
        # print("\tFrame: {} ; is_last_frame: {}".format(frame, is_last_frame))
        pass

    def processTextMessage(self, message):
        # print("processTextMessage - message: {}".format(message))
        # if self.clientConnection:
        #     for client in self.clients:
        #         # if client!= self.clientConnection:
        #         client.sendTextMessage(message)
        #         client.sendTextMessage("CHICKEN")
        pass
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
        try:
            content = pickle.loads(payload)
            # print(content)
            event_type = content['event']
        except KeyError:
            return print("Payload not formatted correctly!")

        # FIXME this should be a switch statement but it doesn't exist in python 3.9
        if event_type == Events.Connection:
            print("connection update thingy")
            self.initialConnectionInformation(client_socket, content)

        elif event_type == Events.GameStart:
            print("GAME START SIGNAL")
            self.start_game(content['difficulty'])

        elif event_type == Events.BoardGenerated:
            print("Board generation server")
            self.received_board(content)

        elif event_type == Events.TilesRevealed:
            print("Server: Tile received")
            self.received_tiles(content)

        elif event_type == Events.TileFlagged:
            print("Flagged Tile")
            self.received_flag(content)

        elif event_type == Events.GameOver:
            print("Some game ended")
            self.game_over(content)

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
        for client in self.clients:
            content_to_send = self.form_object_to_send(Events.Disconnect, {'user_id': user_id})
            client.sendBinaryMessage(content_to_send)

    # this will emit a username signal back to main to update the user information and stuff
    def initialConnectionInformation(self, client_socket, payload):
        user_id = payload["user_id"]
        username = payload["username"]
        # we'll store all relevant data by their unique id
        self.client_data[user_id] = {
            'socket': client_socket,
            'username': username,
        }
        print("client list!", self.clients)
        print('client data!', self.client_data)
        print(f"Initial data received from {username} \n"
              f"id: {user_id}")
        # this is for the GUI update of player list
        self.player_connected.emit(user_id, username)
        # this is for the actual sockets
        # need to remove socket from data
        formatted_player_data = self.format_player_data()

        for client in self.clients:
            content_to_send = self.form_object_to_send(Events.Connection, formatted_player_data)
            client.sendBinaryMessage(content_to_send)

    def start_game(self, difficulty):
        self.game_counter = 0
        self.winners = {}
        self.losers = {}
        for client in self.clients:
            content = self.form_object_to_send(Events.GameStart, {'difficulty': difficulty})
            client.sendBinaryMessage(content)

    # don't need to format it's already formatted from the client so we just need to repickle
    # it would be more efficient to never unpickle it and just pass it on...
    # I also basically use the same function 3 times with a different name...I should change that...
    def received_board(self, content):
        current_socket = self.sender()
        for client in self.clients:
            if client is not current_socket:
                client.sendBinaryMessage(pickle.dumps(content))

    def received_tiles(self, content):
        current_socket = self.sender()
        for client in self.clients:
            if client is not current_socket:
                client.sendBinaryMessage(pickle.dumps(content))

    def received_flag(self, content):
        current_socket = self.sender()
        for client in self.clients:
            if client is not current_socket:
                client.sendBinaryMessage(pickle.dumps(content))

    def game_over(self, content):
        print("SERVER SEES GAME IS OVER")
        print("Clients", self.clients)
        current_socket = self.sender()
        self.game_counter += 1
        for client in self.clients:
            if client is not current_socket:
                client.sendBinaryMessage(pickle.dumps(content))

        # add to rankings list
        del (content['event'])
        user_id = content['user_id']
        del (content['user_id'])
        # saving time only by user_id
        if content['didWin']:
            del (content['didWin'])
            # leaving with just userId and timer
            self.winners[user_id] = content['time']
            # print("winners", self.winners)
        else:
            del (content['didWin'])
            self.losers[user_id] = content['time']
            # print("losers", self.losers)

        if self.game_counter == len(self.clients):
            print("ALL GAMES ARE FINISHED")
            winners, losers = self.sort_game_overs()
            to_send = self.form_object_to_send(Events.AllFinished, {"winners": winners, "losers": losers})
            for client in self.clients:
                print("ONE")
                client.sendBinaryMessage(to_send)

    # returns a list of tupples (user_id, timer) sorted
    def sort_game_overs(self):
        winners = sorted(self.winners.items(), key=lambda x: x[1])
        # people who lose slower are better...
        losers = sorted(self.losers.items(), key=lambda x: x[1], reverse=True)
        print("SORTED WINNERS", winners)
        print("SORTED LOSERS", losers)
        return winners, losers


    # we need this to remove the socket since that cannot be pickled
    def format_player_data(self):
        content_to_send = {}
        player_count = 0
        for user_id, data in self.client_data.items():
            # current_data = {"player" + str(player_count): {"user_id": user_id, user_id: {'username': data['username']}}}
            current_data = {user_id: {'username': data['username']}}

            # current_data = current_data | {user_id: {'username': data['username']}}
            content_to_send = content_to_send | current_data
            player_count += 1
        return content_to_send

    def form_object_to_send(self, key, content):
        header = {"event": key}
        # this basically zips the dictionaries together by piping one into the other
        content_to_send = header | content
        print(content_to_send)
        # serialize it
        content_bytes = pickle.dumps(content_to_send)
        return content_bytes


if __name__ == '__main__':
    import sys

    # why must this be defined outside of the class??!?!?!?!?!??
    parent = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.NonSecureMode)

    app = QApplication(sys.argv)
    server = MyServer(parent)

    app.exec_()
