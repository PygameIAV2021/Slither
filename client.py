import asyncio
from game import Game
from worm import Worm
from food import Food, foodHolder
import settings

from Message import Message, MesType, ConnectionCodes

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

        elif mes.type == MesType.Position:
            if settings.debug:
                print(f"update position: {mes.mes}")

            wormData = mes.mes['w']
            foodData = mes.mes['f']

            self.updateWorms(wormData)
            self.updateFood(foodData)

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
                self.game.mainWorm.updatedByServer = True
            else:
                exist = False
                for w in self.game.otherWorms:  # type: Worm
                    if w.name == worm_d[Worm.d_name]:
                        w.updateByData(worm_d)
                        exist = True
                        break

                if not exist:
                    worm = Worm(
                        name=worm_d[Worm.d_name],
                        coord=worm_d[Worm.d_head],
                        color=worm_d[Worm.d_color],
                        surface=self.game.surface
                    )
                    worm.updateByData(worm_d)
                    worm.updatedByServer = True
                    self.game.otherWorms.append(worm)

        for w in self.game.otherWorms:  # type: Worm
            if not w.updatedByServer:
                self.game.otherWorms.remove(w)
            else:
                w.updatedByServer = False

    def updateFood(self, foodData: list) -> None:
        """move food, create food or delete food"""

        for food_d in foodData:

            exist = False
            for f in foodHolder:
                if f.id == food_d[Food.d_id]:
                    f.updateByData(food_d)
                    exist = True

            if not exist:

                food = Food(
                    food_d[Food.d_coord],
                    food_d[Food.d_radius],
                    food_d[Food.d_energy],
                    self.game.surface,
                    food_d[Food.d_angle],
                    food_d[Food.d_speed],
                    food_d[Food.d_id]
                )
                food.updatedByServer = True
                foodHolder.append(food)

        for f in foodHolder:
            if not f.updatedByServer:
                foodHolder.remove(f)
                del f
            else:
                f.updatedByServer = False


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
