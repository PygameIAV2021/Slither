from circle import Circle
from random import randint

foodHolder = []


def addFood(surface, screen_resolution):
    foodHolder.append(
        Food(
            coord=[randint(0, screen_resolution[0]), randint(0, screen_resolution[1])],
            radius=10,
            energy=2,
            surface=surface
        )
    )


class Food(Circle):
    def __init__(self, coord, radius, energy, surface):
        super().__init__(coord, radius, (0, 255, 0), surface)
        self.energy = energy
