from circle import Circle
from random import randint
from settings import screen_resolution

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
    def __init__(self, coord, radius, energy, surface):
        super().__init__(coord, radius, (0, 255, 0), surface)
        self.energy = energy

    def move(self):
        self.coord[0] += randint(-3, 3)
        self.coord[1] += randint(-3, 3)

        self.handleOutOfScreen()
