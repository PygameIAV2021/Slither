import pygame
from math import pi, floor
from worm import Worm
from random import randint, random
import food as f
import settings

from Message import Message, MesType
import asyncio
import queue


# user input status bits
class InputStatus:
    a = 1
    d = 2
    a_changed = 4
    d_changed = 8

class Game:
    # setting:
    fullCircle = pi * 2

    def __init__(self, client):

        self.client = client
        self.mainWorm = None

        if "isSinglePlayer" == "nein":
            self.mainWorm = Worm(
                name="player1",
                coord=self.getRandomCoord(),
                color=(0, 0, 255),
                surface=self.surface
            )

    def iniPygame(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('slither')

        self.font = pygame.font.SysFont('default', 20)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(settings.screen_resolution, 0, 32)
        self.run = True


    async def start_multiplayer(self):
        '''start pygame (client side of the multiplayer)'''

        self.iniPygame()
        message = Message(MesType.HelloServer, 'Guten Tag Server')
        print("send: ", message.serialize())

        self.client.sendMess(message)

        while self.mainWorm == None:
            await asyncio.sleep(0.1)

        userInput = 0
        while self.run:

            userInput = self.getInput(userInput)

            message = Message(MesType.Input, userInput)
            print("send: ", message.serialize())
            self.client.sendMess(message)
            userInput &= ~InputStatus.a_changed
            userInput &= ~InputStatus.d_changed

            while not self.client.updatedFromServer:
                await asyncio.sleep(0.0001)

            self.client.updatedFromServer = False
            if not self.client.movedByServer:
                self.move()
                self.client.movedByServer = False
            #self.calc()
            self.draw()

            # max fps
            self.clock.tick(settings.fps)

        pygame.quit()

    def start_singleplayer(self):

        self.iniPygame()
        userInput = 0

        while self.run:

            userInput = self.getInput(userInput)

            message = Message(MesType.Input, userInput)
            print("send: ", message.serialize())
            self.client.sendMessage(message.serialize())
            userInput &= ~InputStatus.a_changed
            userInput &= ~InputStatus.d_changed


            self.move()
            self.calc()
            self.draw()

            # max fps
            self.clock.tick(settings.fps)

        pygame.quit()

    def getInput(self, userInput):

        pKeys = pygame.key.get_pressed()

        changed = False

        if pKeys[pygame.K_a] == 1:

            if userInput & InputStatus.a != InputStatus.a:
                userInput |= InputStatus.a_changed
            userInput |= InputStatus.a

            self.mainWorm.angle -= settings.worm['turnAngle']
            changed = True
        elif userInput & InputStatus.a == InputStatus.a:
            userInput |= InputStatus.a_changed
            userInput &= ~InputStatus.a

        if pKeys[pygame.K_d] == 1:

            if userInput & InputStatus.d != InputStatus.d:
                userInput |= InputStatus.d_changed

            userInput |= InputStatus.d

            self.mainWorm.angle += settings.worm['turnAngle']
            changed = True
        elif userInput & InputStatus.d == InputStatus.d:
            userInput |= InputStatus.d_changed
            userInput &= ~InputStatus.d

        if changed:
            self.mainWorm.angle %= self.fullCircle

        try:
            next(event for event in pygame.event.get() if event.type == pygame.QUIT)
            self.run = False
        except StopIteration:
            pass

        return userInput

    def calc(self):

        if len(f.foodHolder) <= settings.maxNumberOfFood and random() > 0.97:
            f.addFood(self.surface)

        self.checkCollisionWithFood()

    def move(self):
        self.mainWorm.move()
        for food in f.foodHolder:
            food.move()

    def draw(self):
        self.surface.fill((255, 255, 255))

        # display fps:
        fpsText = self.font.render('FPS: ' + str(floor(self.clock.get_fps())), False, (0, 0, 0))
        self.surface.blit(fpsText, (0, 0))

        for food in f.foodHolder:
            food.draw()

        self.mainWorm.draw()

        pygame.display.update()

    def checkCollisionWithFood(self):
        head = self.mainWorm.getHead()

        for food in f.foodHolder:
            if food.checkCollision(head):
                self.mainWorm.eat(food)
                f.foodHolder.remove(food)
                del food
                break

    def getRandomCoord(self):
        return [
            randint(settings.spawnDistanceToBorder, settings.screen_resolution[0] - settings.spawnDistanceToBorder),
            randint(settings.spawnDistanceToBorder, settings.screen_resolution[1] - settings.spawnDistanceToBorder)
        ]