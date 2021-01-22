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
    def __init__(self, coord, radius, energy, surface, angle = 0, speed = default_food['speed'], id = None):
        super().__init__(coord, radius, (0, 255, 0), surface, angle, speed)
        self.energy = energy
        if self.angle == 0:
            self.angle = random() * 2*math.pi
        self.vector = []
        self.vector.append(math.cos(self.angle) * self.speed)
        self.vector.append(math.sin(self.angle) * self.speed)

        if id == None:
            self.id = Food.id_counter
            Food.id_counter += 1
        else:
            self.id = id

        self.updatedByServer = False

    id_counter = 0

    def move(self, newAngle = None):

        if newAngle is not None:
            self.angle = newAngle
            self.vector[0] = math.cos(self.angle) * self.speed
            self.vector[1] = math.sin(self.angle) * self.speed

        self.coord[0] += self.vector[0]
        self.coord[1] += self.vector[1]

        self.handleOutOfScreen()

    d_coord = 0
    d_radius = 1
    d_energy = 2
    d_angle = 3
    d_speed = 4
    d_id = 5

    def generateData(self):
        data = {
            Food.d_coord: self.coord,
            Food.d_radius: self.radius,
            Food.d_energy: self.energy,
            Food.d_angle: self.angle,
            Food.d_speed: self.speed,
            Food.d_id: self.id,
        }

        return data

    def updateByData(self, data):
        self.coord = data[Food.d_coord]
        self.radius = data[Food.d_radius]
        self.energy = data[Food.d_energy]
        self.angle = data[Food.d_angle]
        self.speed = data[Food.d_speed]

        self.updatedByServer = True
