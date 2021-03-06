from math import pi, floor
from scripts.food import foodHolder
import scripts.settings as settings
from scripts.Message import Message, MesType
import asyncio


class InputStatus:
    """user input status bits"""
    a = 1
    d = 2


def checkFoodTTL():
    for f in foodHolder:  # type: Food
        f.ttl -= 1
        if f.ttl < 1:
            foodHolder.remove(f)
            del f
            continue


class Game:
    """The game class. For drawing and calculations"""

    # setting:
    fullCircle = pi * 2

    def __init__(self, client):

        self.client = client
        self.otherWorms = []
        self.mainWorm = None

    def iniPygame(self) -> None:
        """initial pygame"""

        import pygame

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('slither')

        self.font = pygame.font.SysFont('default', 20)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(settings.screen_resolution, 0, 32)
        self.run = True

    async def start_multiplayer(self) -> None:
        """called by the client. say hello to server, start the game loop and send inputs to the server"""

        self.iniPygame()
        message = Message(MesType.HelloServer, 'Guten Tag Server')
        if settings.debug:
            print("send: ", message.serialize())

        self.client.sendMess(message)

        while self.mainWorm is None:
            await asyncio.sleep(0.1)

        userInput = 0
        while self.run:

            userInput = self.getInput(userInput)

            message = Message(MesType.Input, userInput)
            if settings.debug:
                print("send: ", message.mes)
            self.client.sendMess(message)

            while not self.client.updatedByServer:
                await asyncio.sleep(0.0001)

            self.client.updatedByServer = False

            checkFoodTTL()
            self.move()
            self.client.movedByServer = False
            self.draw()

            # max fps
            self.clock.tick(settings.fps)

        import pygame
        pygame.quit()
        self.client.sendClose()
        raise KeyboardInterrupt

    def getInput(self, userInput: int) -> int:
        """check the pygame events and set userInput. Also change the mainWorm angle"""

        import pygame
        pKeys = pygame.key.get_pressed()

        changed = False

        if pKeys[pygame.K_a] or pKeys[pygame.K_LEFT]:
            userInput |= InputStatus.a
            self.mainWorm.angle -= settings.defaultWorm['turnAngle']
            changed = True
        elif userInput & InputStatus.a == InputStatus.a:
            userInput &= ~InputStatus.a
        if pKeys[pygame.K_d] or pKeys[pygame.K_RIGHT]:
            userInput |= InputStatus.d
            self.mainWorm.angle += settings.defaultWorm['turnAngle']
            changed = True
        elif userInput & InputStatus.d == InputStatus.d:
            userInput &= ~InputStatus.d

        if changed:
            self.mainWorm.angle %= self.fullCircle

        try:
            next(event for event in pygame.event.get() if event.type == pygame.QUIT)
            self.run = False
        except StopIteration:
            pass

        return userInput

    def move(self) -> None:
        """only called on the client side"""

        for worm in self.otherWorms:
            if worm.movedByServer:
                worm.movedByServer = False
            else:
                worm.move()

        if self.mainWorm.movedByServer:
            self.mainWorm.movedByServer = False
        else:
            self.mainWorm.move()

        for food in foodHolder:
            food.move()

    def draw(self) -> None:
        """draw the worms, foods and the background"""

        import pygame
        self.surface.fill((0, 0, 0))

        # display fps:
        fpsText = self.font.render('FPS: ' + str(floor(self.clock.get_fps())), False, (255, 255, 255))
        self.surface.blit(fpsText, (0, 0))

        for food in foodHolder:
            food.draw()

        for otherWorms in self.otherWorms:
            otherWorms.draw()

        self.mainWorm.draw()

        pygame.display.update()
