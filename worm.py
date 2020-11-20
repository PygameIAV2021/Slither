#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:28:45 2020

@author: dustin
"""

from circle import Circle
import math


class Worm:

    def __init__(self, name, coord, surface, color, length=10, radius=10):
        self.name = name

        self.body = []
        self.distance = 3
        self.speed = 2
        self.angle = 0
        self.color = color

        for i in range(1, length):
            circle = Circle(coord, radius, self.color, surface)

            if i == 1:
                circle.color = (255, 0, 0)

            self.body.append(circle)

            coord = [coord[0] - self.distance, coord[1] - self.speed]
            coord = [coord[0] - self.distance, coord[1] - self.speed]

            print(len(self.body))
            print(id(self.body[0].coord))
            print(id(self.body[-1].coord))
            print(coord)

    def move(self, distance = 0):
        oldHead = self.body[0]
        newHead = self.body.pop()

        newHead.color = oldHead.color
        oldHead.color = self.color

        newHead.coord[0] = oldHead.coord[0] + math.cos(self.angle) * (self.speed + distance)
        newHead.coord[1] = oldHead.coord[1] + math.sin(self.angle) * (self.speed + distance)

        self.body.insert(0, newHead)

    def draw(self):
        for circle in self.body[::-1]:
            circle.draw()
