import asyncio
from scripts.game import Game
from scripts.worm import Worm
from scripts.food import Food, foodHolder
import scripts.settings as settings
from scripts.Message import Message, MesType, ConnectionCodes

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory


class SlitherClient(WebSocketClientProtocol):
    """The client webSocket"""

    updatedByServer = False
    game = None

    def onConnect(self, response):
        print("connected to sever: {0}".format(response.peer))

    async def onOpen(self):
        """Start the game when connection established"""

        print("WebSocket connection open.")

        self.game = Game(self)
        await self.game.start_multiplayer()

    def onMessage(self, payload, isBinary):
        """handle the messages from the server. Update the pygame-objects"""

        mes = Message.deserialize(payload)  # type: Message

        if settings.debug:
            print(f"Message received: {mes.mes}")

        if mes.type == MesType.HelloClient:

            self.game.mainWorm = Worm(
                name="you",
                coord=mes.mes[Worm.d_head],
                color=mes.mes[Worm.d_color],
                surface=self.game.surface
            )

            self.game.mainWorm.updateByData(mes.mes)

        elif mes.type == MesType.Position:
            if settings.debug:
                print(f"update position: {mes.mes}")

            wormData = mes.mes

            self.updateWorms(wormData)

        elif mes.type == MesType.NewFood:
            newFood = Food(
                mes.mes[Food.d_coord],
                mes.mes[Food.d_energy],
                self.game.surface,
                mes.mes[Food.d_angle],
                mes.mes[Food.d_speed],
                mes.mes[Food.d_id]
            )
            newFood.color = mes.mes[Food.d_color]
            newFood.radius = mes.mes[Food.d_radius]
            newFood.updatedByServer = True
            foodHolder.append(newFood)

        elif mes.type == MesType.DelFood:
            for f in foodHolder:
                if f.id == mes.mes:
                    foodHolder.remove(f)
                    del(f)
                    break

        elif mes.type == MesType.NewEnemy:
            newWorm = Worm(
                name=mes.mes[Worm.d_name],
                coord=mes.mes[Worm.d_head],
                color=mes.mes[Worm.d_color],
                surface=self.game.surface
            )
            newWorm.updateByData(mes.mes)
            print(f"new player joined! {newWorm.name}")
            self.game.otherWorms.append(newWorm)

        elif mes.type == MesType.YouAreDeath:
            print(f"\nGAME OVER!\nYou were killed! Your score: {len(self.game.mainWorm.body)}")
            raise KeyboardInterrupt
        else:
            print(f"unexpected message! '{mes.type}'")

        self.updatedByServer = True

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {code}")
        if code == ConnectionCodes.serverFull:
            print(f"server is full! Try again later...")
        elif code == ConnectionCodes.youWereKilled:
            print(f"You were killed! Your score: {len(self.game.mainWorm.body)}")
        elif code == ConnectionCodes.protocolError:
            print(f"Protocol error. Perhaps you are running another version")

        raise KeyboardInterrupt

    def sendMess(self, message: Message) -> None:
        """serialize message and send it to the slither-server"""

        self.sendMessage(payload=message.serialize(), isBinary=True)

    def updateWorms(self, wormData: list) -> None:
        """update worm, create worm or delete worm"""

        for worm_d in wormData:
            if worm_d[Worm.d_name] == 'you':
                self.game.mainWorm.updateByData(worm_d)
                #self.game.mainWorm.updatedByServer = True
            else:
                exist = False
                for w in self.game.otherWorms:  # type: Worm
                    if w.name == worm_d[Worm.d_name]:
                        w.updateByData(worm_d)
                        exist = True
                        break

                if not exist:
                    print("this should never be happen!")
                    worm = Worm(
                        name=worm_d[Worm.d_name],
                        coord=worm_d[Worm.d_head],
                        color=worm_d[Worm.d_color],
                        surface=self.game.surface
                    )
                    worm.updateByData(worm_d)
                    #worm.updatedByServer = True
                    self.game.otherWorms.append(worm)

        # if a worm has not been updated by the server, then the client has disconnected -> remove worm from list
        for w in self.game.otherWorms:  # type: Worm
            if not w.updatedByServer:
                self.game.otherWorms.remove(w)
            else:
                w.updatedByServer = False


class Client:
    """The Client. Handle the SlitherClient-webSocket"""

    def __init__(self, host: str, port: int):
        self.__port = port
        self.__host = host
        self.__run = False
        self.__coroutine = None
        self.__loop = None

    def start(self) -> None:
        """start the SlitherClient-webSocket"""

        # creates the autobahn-webSocket-factory and bind the SlitherClient as the protocol
        factory = WebSocketClientFactory(f"ws://{self.__host}:{self.__port}")
        factory.protocol = SlitherClient

        # used the best-practice from the autobahn-webSocket-asyncio documentation:
        self.__loop = asyncio.get_event_loop()
        self.__coroutine = self.__loop.create_connection(factory, self.__host, self.__port)
        self.__loop.run_until_complete(self.__coroutine)

        self.__loop.run_forever()

    def close(self) -> None:
        """close the connection"""

        if self.__loop is asyncio.AbstractEventLoop:
            self.__loop.close()
