import asyncio
import queue

from Message import Message, Command

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

mesToSend = queue.Queue()

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    async def onOpen(self):
        print("WebSocket connection open.")

        message = Message('Dustin', Command.HelloServer, 'lalal')
        print("send: ", message.serialize())
        self.sendMessage(message.serialize())

        # start sending messages every second ..
        while True:
            await asyncio.sleep(1)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class Client:

    def __init__(self, name: str, host: str, port: int):
        self.__name = name
        self.__port = port
        self.__host = host
        self.__mesToSend = queue.Queue()
        self.__run = False
        self.__coroutine = None
        self.__loop = None

    def connect(self):
        factory = WebSocketClientFactory(f"ws://{self.__host}:{self.__port}")
        factory.protocol = MyClientProtocol

        self.__loop = asyncio.get_event_loop()
        self.__coroutine = self.__loop.create_connection(factory, self.__host, self.__port)
        self.__loop.run_until_complete(self.__coroutine)

        self.__loop.run_forever()

    def close(self):
        if self.__loop is asyncio.AbstractEventLoop:
            self.__loop.close()

client = Client('Dustin', 'localhost', 9000)
client.connect()

print('blub')