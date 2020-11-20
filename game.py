import pygame
import math
from worm import Worm


class Game:
    screen_resolution = (500, 500)
    turn_speed = math.pi / 80

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('slither')

        self.font = pygame.font.SysFont('default', 20)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(self.screen_resolution, 0, 32)
        self.mainWorm = Worm(name="player1", coord=[100, 100], color=(0, 0, 255), surface=self.surface)
        self.mainWorm = Worm(name="player1", coord=[100, 100], color=(0, 0, 255), surface=self.surface)
        self.keys = {'a': 0, 'b': 0}

    def start(self):
        running = True

        while running:

            running = self.handle_input()
            self.calc()
            self.draw()

            # max fps
            self.clock.tick(4)

        pygame.quit()

    def handle_input(self):

        pKeys = pygame.key.get_pressed()

        self.keys['a'] = pKeys[pygame.K_a]
        self.keys['d'] = pKeys[pygame.K_d]

        try:
            qEvent = next(event for event in pygame.event.get() if event.type == pygame.QUIT)
            return False
        except StopIteration:
            return True

    def calc(self):
        self.mainWorm.move()
        return 0

    def draw(self):
        self.surface.fill((255, 255, 255))

        # display fps:
        fpsText = self.font.render('FPS: ' + str(math.floor(self.clock.get_fps())), False, (0, 0, 0))
        self.surface.blit(fpsText, (0, 0))

        self.mainWorm.draw()

        pygame.display.update()
