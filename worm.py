#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:28:45 2020

@author: dustin
"""

from circle import Circle
import math
from settings import screen_resolution


class Worm:

    def __init__(self, name, coord, surface, color, angle=0, length=10, radius=10):
        self.name = name

        self.body = []
        self.distance = 10
        self.speed = 2
        self.angle = angle
        self.color = color
        self.surface = surface
        self.radius = radius

        head = Circle(coord, radius, self.color, self.surface)
        head.color = (255, 0, 0) # head color
        self.body.append(head)

        for i in range(1, length):
            self.addBodyPart()

    def move(self):
        oldHead = self.body[0]
        newHead = self.body.pop()

        newHead.color = oldHead.color
        oldHead.color = self.color

        newHead.coord[0] = oldHead.coord[0] + math.cos(self.angle) * (self.speed + self.distance)
        newHead.coord[1] = oldHead.coord[1] + math.sin(self.angle) * (self.speed + self.distance)

        newHead.handleOutOfScreen()

        self.body.insert(0, newHead)

    def draw(self):
        for circle in self.body[::-1]:
            circle.draw()

    def addBodyPart(self):
        """ add an circle object at the end of the body"""
        coord = self.body[-1].coord

        coord = [
            coord[0] - math.cos(self.angle) * (self.speed + self.distance),
            coord[1] - math.sin(self.angle) * (self.speed + self.distance)
        ]

        circle = Circle(coord, self.radius, self.color, self.surface)
        self.body.append(circle)

    def getHead(self):
        return self.body[0]

    def eat(self, food):
        for i in range(1, food.energy):
            self.addBodyPart()
