"""
Created on Tue Nov 10 17:28:45 2020

@author: dustin
"""

from scripts.circle import Circle
from scripts.settings import defaultWorm
import math
from random import random
from scripts.settings import screen_resolution
from scripts.food import FoodType, Food

fullCircle = math.pi * 2


class Worm:
    """The worm-class"""

    def __init__(self, name, coord, surface, color, length=defaultWorm['length']):
        self.name = name

        self.body = []
        self.distance = 13
        self.speed = defaultWorm['speed']
        self.angle = random() * fullCircle
        self.color = color
        self.surface = surface
        self.radius = defaultWorm['radius']
        self.halfScreen = (screen_resolution[0] / 2, screen_resolution[1] / 2)
        self.updatedByServer = False
        self.movedByServer = False
        self.immortal = 300  # the first 300 ticks the worm is immortal and cannot kill somebody else

        head = Circle(coord, self.radius, self.color, self.surface, self.angle, self.speed)

        head.color = defaultWorm['ownHeadColor'] if self.name == 'you' else defaultWorm['enemyHeadColor']

        # the body is a list of circle objects. Index 0 is the head
        self.body.append(head)

        for i in range(1, length):
            self.addBodyPart()

    def move(self) -> None:
        """change the position of the worm by speed and angle"""

        self.body[0].coord[0] += (math.cos(self.angle) * self.speed)
        self.body[0].coord[1] += (math.sin(self.angle) * self.speed)
        self.body[0].handleOutOfScreen()

        for i in range(len(self.body) - 1, 0, -1):

            if self.body[i].getDistanceToCenter(self.body[i - 1]) <= self.radius:
                continue
                # only move if the distance between the two circles is more then self.radius - 2

            distance = [
                self.body[i - 1].coord[0] - self.body[i].coord[0],
                self.body[i - 1].coord[1] - self.body[i].coord[1]
            ]

            # if circle[i] is 'out of screen'/'other side', then make a correction for d.
            # After that i have the correct angle
            for axis in range(2):
                if abs(distance[axis]) >= screen_resolution[axis] - self.body[i].diameter:
                    if self.body[i - 1].coord[axis] > self.halfScreen[axis]:
                        distance[axis] -= screen_resolution[axis]  # left or top out
                    else:
                        distance[axis] += screen_resolution[axis]  # right or bottom out

            angle = math.atan2(distance[1], distance[0])
            angle %= fullCircle
            self.body[i].move(angle)

    def draw(self) -> None:
        """draw each circle in the body"""

        for circle in self.body[::-1]:
            circle.draw()

    def addBodyPart(self) -> None:
        """add an circle object at the end of the body"""

        coord = self.body[-1].coord

        coord = [
             coord[0] - math.cos(self.body[-1].angle) * self.radius / 2,
             coord[1] - math.sin(self.body[-1].angle) * self.radius / 2
        ]

        circle = Circle(coord, self.radius, self.color, self.surface, self.angle, self.speed)
        self.body.append(circle)

    def getHead(self) -> Circle:
        """Returns the head of the worm (first circle object of the body)"""

        return self.body[0]

    def eat(self, food: Food) -> None:
        """Eat the passed food. Grow and do the effects"""

        FoodType.doEffects(self, food.type)
        for i in range(1, food.energy):
            self.addBodyPart()

    def updateSpeed(self, speedFactor: float) -> None:
        """Updates the speed of the worm. Each circle in body has to be updated"""

        newSpeed = self.speed + speedFactor
        if newSpeed > defaultWorm['max_speed']:
            if self.speed == defaultWorm['max_speed']:
                return
            else:
                newSpeed = defaultWorm['max_speed']
        elif newSpeed < defaultWorm['min_speed']:
            if newSpeed == defaultWorm['min_speed']:
                return
            else:
                newSpeed = defaultWorm['min_speed']

        self.speed = newSpeed
        for circle in self.body:
            circle.speed = self.speed

    def updateRadius(self, radiusFactor) -> None:
        """Updates the radius of the worm. Each circle in body has to be updated"""

        newRadius = self.radius + radiusFactor
        if newRadius > defaultWorm['max_radius']:
            if self.radius == defaultWorm['max_radius']:
                return
            else:
                newRadius = defaultWorm['max_radius']
        elif newRadius < defaultWorm['min_radius']:
            if self.radius == defaultWorm['min_radius']:
                return
            else:
                newRadius = defaultWorm['min_radius']

        self.radius = newRadius
        diameter = self.radius * 2
        for circle in self.body:
            circle.radius = self.radius
            circle.diameter = diameter

    # indexes for getData and updateByData (better then strings, for the multiplayer):
    d_head = 0
    d_color = 1
    d_angle = 2
    d_speed = 3
    d_name = 4
    d_body = 5

    def getData(self, all=False) -> dict:
        """generates data of this worm-object for the webSocket-client"""

        data = {
            self.d_head: -1,
            self.d_color: self.color,
            self.d_angle: self.angle,
            self.d_speed: self.speed,
            self.d_name: self.name,
            self.d_body: -1
        }

        if all:
            data[self.d_head] = self.body[0].coord
            data[self.d_body] = []
            for c in self.body:
                data[self.d_body].append(c.getData())

        return data

    def updateByData(self, data) -> None:
        """update this worm-object with the data provided by the webSocket-server"""

        if data[self.d_head] != -1:
            self.body[0].coord = data[self.d_head]
        self.angle = data[self.d_angle]
        self.color = data[self.d_color]
        self.speed = data[self.d_speed]

        if data[self.d_body] != -1:  # in some cases only the head is updated, the rest is calculated by the client self
            self.movedByServer = True
            length = len(data[self.d_body])
            i = 0
            for c in self.body:
                c.updateByData(data[self.d_body][i], updateColor=(i != 0))
                length -= 1
                i += 1
                if length == 0:
                    break

            if length > 0:  # the worm has grown
                while length > 0:
                    circle = Circle(
                        coord=data[self.d_body][i][Circle.d_coord],
                        radius=data[self.d_body][i][Circle.d_radius],
                        color=data[self.d_body][i][Circle.d_color],
                        surface=self.surface, angle=self.angle, speed=self.speed)
                    self.body.append(circle)
                    i += 1
                    length -= 1

        self.updatedByServer = True

