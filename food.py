from circle import Circle
from random import random, randint
from settings import screen_resolution, food as default_food, food_type_factors
import math

foodHolder = []


def addFood(surface) -> None:
    """creates a new food object an add it to the foodHolder-list"""

    foodHolder.append(
        Food(
            coord=[randint(0, screen_resolution[0]), randint(0, screen_resolution[1])],
            radius=10,
            energy=2,
            surface=surface
        )
    )


class FoodType:
    """The class for the different kinds of food. Containing all types, colors and the effects"""

    nothing = 0
    faster = 1
    slower = 2
    bigger = 3
    smaller = 4

    def getColor(foodType):
        """returns the color for the foodType"""

        if foodType == FoodType.nothing:
            return 255, 255, 255  # white
        elif foodType == FoodType.faster:
            return 255, 0, 0  # red
        elif foodType == FoodType.slower:
            return 0, 0, 255  # blue
        elif foodType == FoodType.bigger:
            return (0, 255, 0) #green
        elif foodType == FoodType.smaller:
            return (255, 255,  0) # yellow
        return None

    def doEffects(worm, type) -> None:
        """Changes the worm attributes by the food-type"""

        if type == FoodType.faster:
            worm.updateSpeed(food_type_factors['faster'])
        elif type == FoodType.slower:
            worm.updateSpeed(food_type_factors['slower'])
        elif type == FoodType.bigger:
            worm.updateRadius(food_type_factors['bigger'])
        elif type == FoodType.smaller:
            worm.updateRadius(food_type_factors['smaller'])


class Food(Circle):
    """Child class from Circle-class"""

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

        self.type = randint(0, food_type_factors['count'])
        self.color = FoodType.getColor(self.type)

        self.updatedByServer = False

    id_counter = 0

    def move(self, newAngle = None) -> None:
        """Moves the food by its speed and angle. You can pass a new angle"""

        if newAngle is not None:
            self.angle = newAngle
            self.vector[0] = math.cos(self.angle) * self.speed
            self.vector[1] = math.sin(self.angle) * self.speed

        self.coord[0] += self.vector[0]
        self.coord[1] += self.vector[1]

        self.handleOutOfScreen()

    # indexes for getData and updateByData (better then strings, for the multiplayer):
    d_coord = 0
    d_radius = 1
    d_energy = 2
    d_angle = 3
    d_speed = 4
    d_id = 5
    d_type = 6
    d_color = 7

    def generateData(self) -> dict:
        """generates data of this food-object for the webSocket-client"""

        data = {
            Food.d_coord: self.coord,
            Food.d_radius: self.radius,
            Food.d_energy: self.energy,
            Food.d_angle: self.angle,
            Food.d_speed: self.speed,
            Food.d_id: self.id,
            Food.d_type: self.type,
            Food.d_color: self.color
        }

        return data

    def updateByData(self, data: dict) -> None:
        """update this food-object with the data provided by the webSocket-server"""

        self.coord = data[Food.d_coord]
        self.radius = data[Food.d_radius]
        self.energy = data[Food.d_energy]
        self.angle = data[Food.d_angle]
        self.speed = data[Food.d_speed]
        self.type = data[Food.d_type]
        self.color = data[Food.d_color]

        self.updatedByServer = True
