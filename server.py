import asyncio
from Message import Message, MesType
from worm import Worm
from game import Game, InputStatus
from food import foodHolder, addFood, Food
from random import randint, random
import settings as settings
import time


#todo: ich prüfe wie lange der letzte request her ist. dann bewege ich alle anhand der letzten Zeit und versende alles
#todo: broadcast system einbauen

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


def getRandomColor():
    c = randint(0, len(settings.multiplayer_colors) - 1)
    return settings.multiplayer_colors.pop(c)


def addRandomColor(c):
    settings.multiplayer_colors.append(c)


def getRandomCoord():
    return [
        randint(settings.spawnDistanceToBorder, settings.screen_resolution[0] - settings.spawnDistanceToBorder),
        randint(settings.spawnDistanceToBorder, settings.screen_resolution[1] - settings.spawnDistanceToBorder)
    ]


class ConnectedClient:
    def __init__(self, name):
        self.name = name
        self.worm = Worm(
            name=self.name,
            coord=getRandomCoord(),
            color=getRandomColor(),
            surface=None
        )

class MyServerProtocol(WebSocketServerProtocol):
    clients = []
    worms = []
    game = Game('foo')

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        if len(self.clients) >= settings.multiplayer_max_players:
            self.sendClose(code=settings.ConnectionCodes.serverFull)

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            return

        message = Message.deserialize(payload)

        if settings.debug:
            print(f"message received: command:{message.type}, mes: '{message.mes}'")

        answer = None
        playerName = self.getClientName()
        client = None

        if message.type == MesType.HelloServer:
            if playerName not in self.clients:
                client = ConnectedClient(playerName)
                self.clients.append(client)

                print("create new worm for " + playerName)
                answer = Message(MesType.HelloClient, client.worm.getData(all=True))

        elif message.type == MesType.Input:

            if settings.debug:
                print(f"get input from client: {message.mes}")
            client = self.getClient(playerName)

            self.handleInput(message.mes, client.worm)
            client.worm.move()
            answer = Message(MesType.Position, client.worm.getData())

        else:
            print("was ist das für ne Nachricht???")

        if type(answer) is Message:
            if message.type == MesType.Input:
                # self.calc()
                answer = Message(MesType.Position, self.generatePositionDataForPlayer(client))
            self.sendMess(answer)


    def generatePositionDataForPlayer(self, connectedClient: ConnectedClient):
        worms_data = []
        for client in self.clients:  # type: ConnectedClient
            if client.name != connectedClient.name:
                worms_data.append(client.worm.getData(all=True))

        yourWorm = connectedClient.worm.getData()
        yourWorm[Worm.d_name] = 'you'
        worms_data.append(yourWorm)

        return worms_data

    def sendMess(self, mess: Message):
        if settings.debug:
            print(f"send message: {mess.type} {mess.mes}")
        self.sendMessage(mess.serialize(), isBinary=True)

    def onClose(self, wasClean, code, reason):
        client = self.getClient(self.getClientName())
        self.clients.remove(client)
        addRandomColor(client.worm.color)
        print("WebSocket connection closed {0}: code {1}".format(self.getClientName(), code))

    def getClientName(self):
        return self.peer.__str__()

    def getClient(self, name):
        return next(c for c in self.clients if c.name == name)  # type: ConnectedClient

    def handleInput(self, input, worm):
        if input & InputStatus.a == InputStatus.a:
            worm.angle -= settings.worm['turnAngle']
        if input & InputStatus.d == InputStatus.d:
            worm.angle += settings.worm['turnAngle']

    def calc(self, worm: Worm):
        """in progress"""
        if len(foodHolder) <= settings.maxNumberOfFood and random() > 0.97:
            addFood(None)

        self.checkCollisionWithFood(worm)

    def checkCollisionWithFood(self, worm: Worm):
        """in progress"""
        head = worm.getHead()

        for food in foodHolder:
            if food.checkCollision(head):
                self.mainWorm.eat(food)
                foodHolder.remove(food)
                del food
                break

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
