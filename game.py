import pygame
from math import pi, floor
from worm import Worm
from random import randint, random
import food as f
import settings


class Game:
    # setting:
    turn_speed = pi / 80
    fullCircle = pi * 2

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('slither')

        self.font = pygame.font.SysFont('default', 20)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(settings.screen_resolution, 0, 32)

        self.mainWorm = Worm(
            name="player1",
            coord=[
                randint(settings.spawnDistanceToBorder, settings.screen_resolution[0] - settings.spawnDistanceToBorder),
                randint(settings.spawnDistanceToBorder, settings.screen_resolution[1] - settings.spawnDistanceToBorder)
            ],
            color=(0, 0, 255),
            surface=self.surface,
            angle=random() * self.fullCircle
        )

    def start(self):
        running = True

        while running:
            running = self.handle_input()
            self.move()
            self.calc()
            self.draw()

            # max fps
            self.clock.tick(settings.fps)

        pygame.quit()

    def handle_input(self):

        pKeys = pygame.key.get_pressed()

        changed = False

        if pKeys[pygame.K_a] == 1:
            self.mainWorm.angle -= settings.angleDelta
            changed = True
        if pKeys[pygame.K_d] == 1:
            self.mainWorm.angle += settings.angleDelta
            changed = True

        if changed:
            self.mainWorm.angle %= self.fullCircle

        try:
            qEvent = next(event for event in pygame.event.get() if event.type == pygame.QUIT)
            return False
        except StopIteration:
            return True

    def calc(self):

        if len(f.foodHolder) <= settings.maxNumberOfFood and random() > 0.97:
            f.addFood(self.surface, settings.screen_resolution)

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
