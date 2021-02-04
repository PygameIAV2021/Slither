import asyncio
from scripts.Message import Message, MesType, ConnectionCodes
from scripts.worm import Worm
from scripts.game import Game, InputStatus
from scripts.food import foodHolder, addFood, Food
from random import randint, random
import scripts.settings as settings
from scripts.circle import Circle
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


def getRandomColor() -> tuple:
    """returns and reserve a color for a connected client"""

    c = randint(0, len(settings.multiplayer_colors) - 1)
    return settings.multiplayer_colors.pop(c)


def addRandomColor(c):
    """add an color for future clients"""

    settings.multiplayer_colors.append(c)


def getRandomCoord() -> list:
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


def generateFoodPositionData() -> list:
    """generate position data of all foods"""

    return [f.getData() for f in foodHolder]


def handleInput(cInput: int, client: ConnectedClient) -> None:
    """Handle the keyboard input from a client. Changes the angle of the worm"""

    if cInput & InputStatus.a == InputStatus.a:
        client.worm.angle -= settings.defaultWorm['turnAngle']
    if cInput & InputStatus.d == InputStatus.d:
        client.worm.angle += settings.defaultWorm['turnAngle']


class SlitherServer(WebSocketServerProtocol):
    """The server-logic for the game"""

    clients = []
    worms = []
    game = Game(None)
    cached_foodPosition = None

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary) -> None:
        if not isBinary:
            return

        message = Message.deserialize(payload)

        if settings.debug:
            print(f"message received: command:{message.type}, mes: '{message.mes}'")

        playerName = self.getClientName()

        if message.type == MesType.HelloServer:
            if playerName not in self.clients:
                if len(self.clients) >= settings.multiplayer_max_players:
                    print("server is full! disconnect client")
                    self.sendClose(code=ConnectionCodes.serverFull)
                    return
                client = ConnectedClient(playerName, self)
                self.clients.append(client)
                print("create new worm for " + playerName)
                print(f"number of connected clients: {len(self.clients)}\n")
                wormData = client.worm.getData(all=True)

                for c in self.clients:  # type: ConnectedClient
                    if c.name != client.name:
                        # send the new worm to all clients:
                        c.ws.sendMess(Message(MesType.NewEnemy, wormData))
                        # send the other worms to the connected client:
                        self.sendMess(Message(MesType.NewEnemy, c.worm.getData(all=True)))

                for f in foodHolder:  # send all food objects to the new client
                    self.sendMess(Message(MesType.NewFood, f.getData()))

                answer = Message(MesType.HelloClient, wormData)
                self.sendMess(answer)

        elif message.type == MesType.Input:

            if settings.debug:
                print(f"get input from client: {message.mes}")
            client = self.getClient(playerName)  # type: ConnectedClient
            if not client:
                return

            client.updateCompleteWorm = False

            if client.worm.immortal > 0:
                client.worm.immortal -= 1

            handleInput(message.mes, client)

            client.updated = True

            for c in self.clients:  # type: ConnectedClient
                if not c.updated:
                    return

            # this client is the last one who sent something to the server -> he triggers the broadcast to all clients
            self.calc()
            self.sendPosToAllClients()

        else:
            print("unexpected message!")
            self.sendClose(code=ConnectionCodes.protocolError)

    def calc(self) -> None:
        """calculates the moves and collisions"""

        for f in foodHolder:  # type: Food
            f.ttl -= 1
            if f.ttl < 1:
                foodHolder.remove(f)
                del f
                continue
            f.move()

        for client in self.clients:
            client.worm.move()
            self.checkCollisionWithFood(client)

        for client in self.clients:
            self.checkCollisionWithOtherWorm(client)

        if len(foodHolder) <= settings.maxNumberOfFood and random() > 0.97:
            food = addFood(None)
            for client in self.clients:
                client.ws.sendMess(Message(MesType.NewFood, food.getData()))

    def checkCollisionWithFood(self, client: ConnectedClient):
        """Check if the head of the worm of the client collide with a food.
            If collision detected: call worm.eat and remove food from foodHolder-list.
        """

        head = client.worm.getHead()

        for food in foodHolder:
            if food.checkCollision(head):
                for c in self.clients:
                    c.ws.sendMess(Message(MesType.DelFood, food.id))
                client.worm.eat(food)
                client.updateCompleteWorm = True
                foodHolder.remove(food)
                del food
                break

    def generateWormPositionData(self, connectedClient: ConnectedClient) -> list:
        """generate position data of all worms for a specified client (connectedClient)"""

        worms_data = []
        for client in self.clients:  # type: ConnectedClient
            if client.name != connectedClient.name:
                worms_data.append(client.worm.getData(all=client.updateCompleteWorm))

        yourWorm = connectedClient.worm.getData(all=connectedClient.updateCompleteWorm)
        yourWorm[Worm.d_name] = 'you'
        worms_data.append(yourWorm)

        return worms_data

    def sendMess(self, mess: Message) -> None:
        """send message to the client"""

        if settings.debug:
            print(f"send message: {mess.type} {mess.mes}")
        self.sendMessage(mess.serialize(), isBinary=True)

    def sendPosToAllClients(self) -> None:
        """send positions of objects to all clients"""

        for client in self.clients:
            client.updated = False

        for client in self.clients:
            answer = Message(MesType.Position, self.generateWormPositionData(client))
            client.ws.sendMess(answer)

    def onClose(self, wasClean, code, reason) -> None:
        """Handle the webSocket-onClose event.
            Remove the client from the list and make his color available for new incoming connections.
        """

        client = self.getClient(self.getClientName())
        if client:
            self.clients.remove(client)
            addRandomColor(client.worm.color)

        print(f"WebSocket connection closed {self.getClientName()}: code {code}\t\t{len(self.clients)} players left")

        for c in self.clients:  # type: ConnectedClient
            if not c.updated:
                return

        # received input from each client, yet -> calc the move and collision -> send positions
        self.calc()
        self.sendPosToAllClients()

    def getClientName(self) -> str:
        """Returns the unique identifier of a client"""

        return self.peer.__str__()

    def getClient(self, name: str):
        """Try to get a client by name"""

        try:
            return next(c for c in self.clients if c.name == name)  # type: ConnectedClient
        except StopIteration:
            return False

    def checkCollisionWithOtherWorm(self, client: ConnectedClient) -> None:
        """Check if the head of the worm of the connected client collide with another worm.
            If collision detected: Delete the worm of the connected client and close the connection.
            The OnClose-event will trigger.
        """

        if client.worm.immortal > 0:
            return

        collision = False
        for opponentClient in self.clients:  # type: ConnectedClient
            if opponentClient.worm.immortal > 0:
                continue
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
                    client.ws.sendClose(code=ConnectionCodes.youWereKilled)
                    break


def runServer(argv):
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

    if len(argv) > 1:
        port = argv[1]

    factory = WebSocketServerFactory(f"ws://127.0.0.1:{port}")
    factory.protocol = SlitherServer

    # used the best-practice from the autobahn-webSocket-asyncio documentation:
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(factory, '0.0.0.0', port)
    server = loop.run_until_complete(coroutine)

    print(f"start Slither server on {get_ip()}:{port} ...")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

    print(f"server closed")
