from circle import Circle
from random import random, randint
from settings import screen_resolution, food as default_food
import math

foodHolder = []


def addFood(surface):
    foodHolder.append(
        Food(
            coord=[randint(0, screen_resolution[0]), randint(0, screen_resolution[1])],
            radius=10,
            energy=2,
            surface=surface
        )
    )

# todo: different kinds of food (faster, slower, change move radius)


class Food(Circle):
    def __init__(self, coord, radius, energy, surface, angle = 0):
        super().__init__(coord, radius, (0, 255, 0), surface, angle, default_food['speed'])
        self.energy = energy
        if self.angle == 0:
            self.angle = random() * 2*math.pi
        self.vector = []
        self.vector.append(math.cos(self.angle) * self.speed)
        self.vector.append(math.sin(self.angle) * self.speed)

    def move(self, newAngle = None):

        if newAngle is not None:
            self.angle = newAngle
            self.vector[0] = math.cos(self.angle) * self.speed
            self.vector[1] = math.sin(self.angle) * self.speed

        self.coord[0] += self.vector[0]
        self.coord[1] += self.vector[1]

        self.handleOutOfScreen()
