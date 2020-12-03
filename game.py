import pygame
from math import pi, floor
from worm import Worm
from random import randint, random
import food as f


class Game:
    # setting:
    screen_resolution = (1200, 1200)
    turn_speed = pi / 80
    fullCircle = pi * 2
    fps = 10
    angleDelta = 0.3
    spawnDistanceToBorder = 200

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('slither')

        self.font = pygame.font.SysFont('default', 20)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(self.screen_resolution, 0, 32)

        self.mainWorm = Worm(
            name="player1",
            coord=[
                randint(self.spawnDistanceToBorder, self.screen_resolution[0] - self.spawnDistanceToBorder),
                randint(self.spawnDistanceToBorder, self.screen_resolution[1] - self.spawnDistanceToBorder)
            ],
            color=(0, 0, 255),
            surface=self.surface,
            angle=random() * self.fullCircle
        )

    def start(self):
        running = True

        while running:
            running = self.handle_input()
            self.calc()
            self.draw()

            # max fps
            self.clock.tick(self.fps)

        pygame.quit()

    def handle_input(self):

        pKeys = pygame.key.get_pressed()

        changed = False

        if pKeys[pygame.K_a] == 1:
            self.mainWorm.angle -= self.angleDelta
            changed = True
        if pKeys[pygame.K_d] == 1:
            self.mainWorm.angle += self.angleDelta
            changed = True

        if changed:
            self.mainWorm.angle %= self.fullCircle

        try:
            qEvent = next(event for event in pygame.event.get() if event.type == pygame.QUIT)
            return False
        except StopIteration:
            return True

    def calc(self):
        self.mainWorm.move()

        if random() > 0.97:
            f.addFood(self.surface, self.screen_resolution)

        return 0

    def draw(self):
        self.surface.fill((255, 255, 255))

        # display fps:
        fpsText = self.font.render('FPS: ' + str(floor(self.clock.get_fps())), False, (0, 0, 0))
        self.surface.blit(fpsText, (0, 0))

        for food in f.foodHolder:
            food.draw()

        self.mainWorm.draw()

        pygame.display.update()
