import asyncio
import queue
from game import Game
from worm import Worm

from Message import Message, MesType

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

mesToSend = queue.Queue()


class MyClientProtocol(WebSocketClientProtocol):
    updatedFromServer = False
    movedByServer = False
    game = None

    def onConnect(self, response):
        print("connected to sever: {0}".format(response.peer))

    async def onOpen(self):
        print("WebSocket connection open.")

        self.game = Game(self)
        await self.game.start_multiplayer()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Message received: {0}".format(payload.decode('utf8')))


        mes = Message.deserialize(payload)  # type: Message

        if mes.type == MesType.HelloClient:
            self.game.mainWorm = Worm(
                name="ich",
                coord=mes.mes['head'],
                color=mes.mes['color'],
                surface=self.game.surface
            )
            print(mes.mes)
        elif mes.type == MesType.Position:
            print(f"update position: {mes.mes}")
            for worm in mes.mes:
                if worm['name'] != 'you':
                    self.handleOtherWorm(worm)
                else:
                    self.game.mainWorm.updateByData(worm)
                    if worm['head'] != -1:
                        self.movedByServer = True
                    self.updatedFromServer = True


        getMessage = True

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def sendMess(self, message: Message):
        self.sendMessage(payload=message.serialize(), isBinary=True)

    def startGame(self):
        pass

    def handleOtherWorm(self, otherWormData):
        worm = next((worm for worm in self.game.otherWorms if worm.name == otherWormData['name']), False)
        if worm:
            worm.updateByData(otherWormData)
        else:
            newWorm = Worm(
                name=otherWormData['name'],
                coord=otherWormData['head'],
                color=otherWormData['color'],
                surface=self.game.surface
            )
            self.game.otherWorms.append(newWorm)

class Client:

    def __init__(self, name: str, host: str, port: int):
        self.__name = name
        self.__port = port
        self.__host = host
        self.__mesToSend = queue.Queue()
        self.__run = False
        self.__coroutine = None
        self.__loop = None

    def start(self):
        factory = WebSocketClientFactory(f"ws://{self.__host}:{self.__port}")
        factory.protocol = MyClientProtocol

        self.__loop = asyncio.get_event_loop()
        self.__coroutine = self.__loop.create_connection(factory, self.__host, self.__port)
        self.__loop.run_until_complete(self.__coroutine)

        self.__loop.run_forever()

    def close(self):
        if self.__loop is asyncio.AbstractEventLoop:
            self.__loop.close()


#client = Client('Dustin', '192.168.178.9', 9000)
client = Client('Dustin', '127.0.0.1', 9000)
client.start()

print('blub')
