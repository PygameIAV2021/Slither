"""
Created on Tue Nov 10 17:41:55 2020

@author: dustin
"""

import math
from scripts.settings import screen_resolution


class Circle:
    """The Circle-class"""

    def __init__(self, coord, radius, color, surface, angle, speed):
        self.coord = coord
        self.radius = radius
        self.diameter = radius * 2
        self.color = color
        self.surface = surface
        self.angle = angle
        self.speed = speed

    def move(self, newAngle = None) -> None:
        """change the position of this circle by speed and angle"""

        if newAngle is not None:
            self.angle = newAngle

        self.coord[0] += math.cos(self.angle) * self.speed
        self.coord[1] += math.sin(self.angle) * self.speed
        self.handleOutOfScreen()

    def draw(self) -> None:
        """draw this circle. Uses the pygame.draw.circle"""

        import pygame.draw
        pygame.draw.circle(self.surface, self.color, (math.floor(self.coord[0]), math.floor(self.coord[1])),
                           self.radius)

    def checkCollision(self, other_circle) -> bool:
        """checks if this circle-object collide with other_circle-object"""

        return self.getDistanceBorder(other_circle) <= 0

    def getDistanceBorder(self, other_circle) -> float:
        """returns the distance between the circle borders"""

        return self.getDistanceToCenter(other_circle) - self.radius - other_circle.radius

    def getDistanceToCenter(self, other_circle) -> float:
        """returns the distance between the circle centers"""

        diffX = self.coord[0] - other_circle.coord[0]
        diffY = self.coord[1] - other_circle.coord[1]
        return math.sqrt(diffX ** 2 + diffY ** 2)

    def handleOutOfScreen(self) -> None:
        """when the circle is out of screen, set it to the opposite side"""

        for axis in range(2):
            if self.coord[axis] > screen_resolution[axis]:
                self.coord[axis] -= screen_resolution[axis]
            elif self.coord[axis] < 0:
                self.coord[axis] += screen_resolution[axis]

    # indexes for getData and updateByData (better then strings, for the multiplayer):
    d_radius = 0
    d_color = 1
    d_coord = 3
    d_speed = 4

    def getData(self) -> dict:
        """generates data of this circle-object for the webSocket-client"""

        return {
            self.d_color: self.color,
            self.d_radius: self.radius,
            self.d_coord: self.coord,
            self.d_speed: self.speed
        }

    def updateByData(self, data: dict, updateColor=True) -> None:
        """update this food-object with the data provided by the webSocket-server"""

        self.radius = data[self.d_radius]
        self.diameter = self.radius * 2
        self.coord = data[self.d_coord]
        self.speed = data[self.d_speed]
        if updateColor:
            self.color = data[self.d_color]
