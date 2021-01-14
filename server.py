import asyncio
from Message import Message, MesType
from worm import Worm
from game import Game, InputStatus
import settings as settings
import time

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):
    clients = []
    worms = []
    game = Game('foo')
    counter = 0
    receivedInputs = 0
    inputReceivedFrom = []

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            return

        # todo: reciev message, handle message, send position of anything

        message = Message.deserialize(payload)

        print(f"message received: command:{message.type}, mes: '{message.mes}'")

        answer = None
        index = None
        playerName = self.getClientName()

        if message.type == MesType.HelloServer:
            if playerName not in self.clients:
                self.clients.append(playerName)
                newWorm = Worm(
                    name=playerName,
                    coord=self.game.getRandomCoord(),
                    color=(0, 0, 255),
                    surface=None
                )
                self.worms.append(newWorm)
                index = self.worms.index(newWorm)
                self.inputReceivedFrom.append(0)
                print("create new client " + playerName)
                answer = Message(MesType.HelloClient, newWorm.getData(all=True))

        elif message.type == MesType.Input:
            #todo:
            # 1. get the worm
            # 2. handle input, change worm-angle
            # 2. generate message to send
            # 3. move worm (so the client and the server moves the worm.
            #               i don't have to trasmit a lot of data and the client cannot cheat)
            # 4. send data



            print(f"get input from client: {message.mes}")
            worm = next(w for w in self.worms if w.name == playerName) # type: Worm
            index = self.worms.index(worm)
            self.handleInput(message.mes, worm)
            answer = Message(MesType.Position, worm.getData())

        if index is not None:
            self.inputReceivedFrom[index] = 1

        if type(answer) is Message:
            while message.type == MesType.Input and not self.isInputFromEachClient():
                time.sleep(0.0001)
            self.sendMess(answer)
        for client, value in enumerate(self.inputReceivedFrom):
            if value == 1:
                self.inputReceivedFrom[client] = 0

    def isInputFromEachClient(self):
        for value in enumerate(self.inputReceivedFrom):
            if value == 1:
                return False
        return True

    def sendMess(self, mess: Message):
        print(f"send message: {mess.type} {mess.mes}")
        self.sendMessage(mess.serialize(), isBinary=True)

    def onClose(self, wasClean, code, reason):
        #self.inputReceivedFrom will crash after dissconect
        playerName = self.getClientName()
        if playerName in self.clients:
            self.clients.remove(playerName)
            self.worms = [w for w in self.worms if w.name != playerName]
        print("WebSocket connection closed {0}: {1}".format(self.getClientName(), reason))

    def getClientName(self):
        return self.peer.__str__()

    def handleInput(self, input, worm):
        if input & InputStatus.a == InputStatus.a:
            worm.angle -= settings.worm['turnAngle']
        if input & InputStatus.d == InputStatus.d:
            worm.angle += settings.worm['turnAngle']

if __name__ == '__main__':

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
