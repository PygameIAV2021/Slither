import asyncio
from Message import Message, MesType
from worm import Worm
from game import Game, InputStatus
from food import foodHolder, addFood, Food
from random import randint, random
import settings as settings
from circle import Circle


from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


def getRandomColor():
    """returns and reserve a color for a connected client"""
    c = randint(0, len(settings.multiplayer_colors) - 1)
    return settings.multiplayer_colors.pop(c)


def addRandomColor(c):
    """add an color for future clients"""
    settings.multiplayer_colors.append(c)


def getRandomCoord():
    """returns valid random coord"""
    return [
        randint(settings.spawnDistanceToBorder, settings.screen_resolution[0] - settings.spawnDistanceToBorder),
        randint(settings.spawnDistanceToBorder, settings.screen_resolution[1] - settings.spawnDistanceToBorder)
    ]


class ConnectedClient:
    """A connected Client and his information and status"""
    def __init__(self, name, websocket):
        self.name = name
        self.worm = Worm(
            name=self.name,
            coord=getRandomCoord(),
            color=getRandomColor(),
            surface=None
        )
        self.updated = False
        self.ws = websocket
        self.updateCompleteWorm = False


class SlitherServer(WebSocketServerProtocol):
    """The server-logic for the game"""
    clients = []
    worms = []
    game = Game('foo')
    cached_foodPosition = None


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

        playerName = self.getClientName()

        if message.type == MesType.HelloServer:
            if playerName not in self.clients:
                client = ConnectedClient(playerName, self)
                self.clients.append(client)
                print("create new worm for " + playerName)
                print(f"number of connected clients: {len(self.clients)}\n")
                answer = Message(MesType.HelloClient, client.worm.getData(all=True))
                self.sendMess(answer)

        elif message.type == MesType.Input:

            if settings.debug:
                print(f"get input from client: {message.mes}")
            client = self.getClient(playerName)  # type: ConnectedClient
            if not client:
                return

            client.updateCompleteWorm = False

            self.handleInput(message.mes, client.worm)

            client.updated = True

            for c in self.clients:  # type: ConnectedClient
                if not c.updated:
                    return

            # this client is the last one who sent to the server -> he triggers the broadcast to all clients
            self.calc()
            self.sendPosToAllClients()

        else:
            print("unexpected message!")

    def calc(self):
        """calculates the moves and collisions"""

        for f in foodHolder:  # type: Food
            f.move()

        for client in self.clients:
            client.worm.move()

            self.checkCollisionWithFood(client)

        for client in self.clients:
            self.checkCollisionWithOtherWorm(client)

        if len(foodHolder) <= settings.maxNumberOfFood and random() > 0.97:
            addFood(None)

    def generatePositionDataForPlayer(self, connectedClient: ConnectedClient):
        """generates the position-data for the message to the 'connectedClient'"""
        return {
            'w': self.generateWormPositionData(connectedClient),
            'f': self.generateFoodPositionData()
        }

    def generateWormPositionData(self, connectedClient: ConnectedClient):
        """generate position data of all worms for a specified client (connectedClient)"""
        worms_data = []
        for client in self.clients:  # type: ConnectedClient
            if client.name != connectedClient.name:
                worms_data.append(client.worm.getData(all=True))

        yourWorm = connectedClient.worm.getData(all=connectedClient.updateCompleteWorm)
        yourWorm[Worm.d_name] = 'you'
        worms_data.append(yourWorm)

        return worms_data

    def generateFoodPositionData(self):
        """generate position data of all foods"""

        return [f.generateData() for f in foodHolder]

    def sendMess(self, mess: Message):
        if settings.debug:
            print(f"send message: {mess.type} {mess.mes}")
        self.sendMessage(mess.serialize(), isBinary=True)

    def sendPosToAllClients(self):
        """send positions of objects to all clients"""
        for client in self.clients:
            client.updated = False

        for client in self.clients:
            answer = Message(MesType.Position, self.generatePositionDataForPlayer(client))
            client.ws.sendMess(answer)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed {0}: code {1}".format(self.getClientName(), code))
        client = self.getClient(self.getClientName())
        if client:
            self.clients.remove(client)
            addRandomColor(client.worm.color)

        for c in self.clients:  # type: ConnectedClient
            if not c.updated:
                return

        # received input from each client -> calc the move and collision -> send positions
        self.calc()
        self.sendPosToAllClients()


    def getClientName(self):
        """returns the unique identifier of a client"""
        return self.peer.__str__()

    def getClient(self, name):
        try:
            return next(c for c in self.clients if c.name == name)  # type: ConnectedClient
        except StopIteration:
            return False

    def handleInput(self, input, worm):
        if input & InputStatus.a == InputStatus.a:
            worm.angle -= settings.defaultWorm['turnAngle']
        if input & InputStatus.d == InputStatus.d:
            worm.angle += settings.defaultWorm['turnAngle']

    def checkCollisionWithFood(self, client: ConnectedClient):
        """in progress"""
        head = client.worm.getHead()

        for food in foodHolder:
            if food.checkCollision(head):
                client.worm.eat(food)
                client.updateCompleteWorm = True
                foodHolder.remove(food)
                del food
                break

    def checkCollisionWithOtherWorm(self, client: ConnectedClient):

        collision = False
        for opponentClient in self.clients:  # type: ConnectedClient
            if opponentClient.name == client.name:
                continue
            if collision:
                break
            head = False

            for opponentCircle in opponentClient.worm.body:  # type: Circle
                if head:
                    head = False
                    continue
                collision = client.worm.body[0].checkCollision(opponentCircle)
                if collision:
                    addRandomColor(client.worm.color)
                    self.clients.remove(client)
                    mess = Message(MesType.YouAreDeath, {"killedBy": opponentClient.name})
                    client.ws.sendMess(mess)
                    client.ws.sendClose(code=settings.ConnectionCodes.youGetKilled)
                    break


if __name__ == '__main__':

    def get_ip():
        """Returns the ip-address of the host"""

        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    # Creates the autobahn-webSocket-factory and bind the SlitherServer as the protocol.
    # How the factory and the SlitherServer works:
    #   If a client connect to the server, the factory provides a new object of the SlitherServer.
    #   So each connection has is own SlitherServer-Object.
    #   The static attributes of the SlitherServer-class are available and synchronised
    #       for all connections.
    #   These SlitherServer-Objects will be deleted if the client disconnect.
    port = 9000
    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = SlitherServer

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    print(f"start Slither server on {get_ip()}:{port} ...")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

    print(f"server closed")
