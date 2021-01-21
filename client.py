import asyncio
import queue
from game import Game
from worm import Worm
import settings

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
        mes = Message.deserialize(payload)  # type: Message

        if settings.debug:
            print(f"Message received: {mes.mes}")

        if mes.type == MesType.HelloClient:

            self.game.mainWorm = Worm(
                name="ich",
                coord=mes.mes[Worm.d_head],
                color=mes.mes[Worm.d_color],
                surface=self.game.surface
            )
        elif mes.type == MesType.Position:
            if settings.debug:
                print(f"update position: {mes.mes}")
            for worm in mes.mes:
                if worm[Worm.d_name] != 'you':
                    self.handleOtherWorm(worm)
                else:
                    self.game.mainWorm.updateByData(worm)
                    if worm[Worm.d_head] != -1:
                        self.movedByServer = True
                    self.updatedFromServer = True
            self.checkIfSomeoneDisconnected()

        getMessage = True

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def sendMess(self, message: Message):
        self.sendMessage(payload=message.serialize(), isBinary=True)

    def startGame(self):
        pass

    def handleOtherWorm(self, otherWormData):
        worm = next((worm for worm in self.game.otherWorms if worm.name == otherWormData[Worm.d_name]), False)
        if worm:
            worm.updateByData(otherWormData)
        else:
            worm = Worm(
                name=otherWormData[Worm.d_name],
                coord=otherWormData[Worm.d_head],
                color=otherWormData[Worm.d_color],
                surface=self.game.surface
            )
            self.game.otherWorms.append(worm)
        worm.updatedByServer = True

    def checkIfSomeoneDisconnected(self):
        for w in self.game.otherWorms:  # type: Worm
            if not w.updatedByServer:
                print(f"someone disconnected! ({w.name})")
                self.game.otherWorms.remove(w)
            else:
                w.updatedByServer = False


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
try:
    client.start()
except KeyboardInterrupt:
    import sys, os
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
