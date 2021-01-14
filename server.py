import asyncio
from Message import Message, MesType

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):
    myClients = []

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            return

        # todo: reciev message, handle message, send position of anything

        message = Message.deserialize(payload.decode('utf8'))

        print(f"message received: command:{message.type}, mes: '{message.mes}', input: {message.userInput}")

        answer = None

        if message.type == MesType.HelloServer:
            if self.peer.__str__() not in self.myClients:
                self.myClients.append(self.peer.__str__())
            answer = Message(MesType.HelloClient, 'Guten Tag Client', )

        elif message.type == MesType.Input:
            print(f"get input from client: {message.mes}")

        if type(answer) is Message:
            self.sendMessage(answer.serialize(), False)

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
