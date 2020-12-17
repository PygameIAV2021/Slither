import asyncio
from Message import Message, Command

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            return
        message = Message.deserialize(payload.decode('utf8'))

        print(f"Text message received: {message.command}")

        response = None

        if message.command == Command.HelloServer:
            print(f"new client '{message.name}'")
            response = Message("server", Command.HelloClient, 'blablabla')

        if type(message) is Message:
            self.sendMessage(response.serialize(), False)


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


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
