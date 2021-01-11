#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:28:45 2020

@author: dustin
"""

from circle import Circle
from settings import worm as defaultWorm
import math
from random import random
from settings import screen_resolution

fullCircle = math.pi * 2

class Worm:

    def __init__(self, name, coord, surface, color, length=defaultWorm['length']):
        self.name = name

        self.body = []
        self.distance = 13
        self.speed = defaultWorm['speed']
        self.angle = random() * fullCircle
        self.color = color
        self.surface = surface
        self.radius = defaultWorm['radius']
        self.halfScreen = (screen_resolution[0]/2, screen_resolution[1]/2)

        head = Circle(coord, self.radius, self.color, self.surface, self.angle, self.speed)
        head.color = (255, 0, 0) # head color
        self.body.append(head)

        for i in range(1, length):
            self.addBodyPart()

    def move(self):
        self.body[0].coord[0] += (math.cos(self.angle) * self.speed)
        self.body[0].coord[1] += (math.sin(self.angle) * self.speed)
        self.body[0].handleOutOfScreen()

        for i in range(len(self.body)-1, 0, -1):

            if self.body[i].getDistanceCenter(self.body[i-1]) <= self.distance:
                continue
                # only move if the distance between the two circles is more then self.distance

            d = [
                self.body[i - 1].coord[0] - self.body[i].coord[0],
                self.body[i - 1].coord[1] - self.body[i].coord[1]
            ]

            # if circle[i] is 'out of screen'/'other side', then make a correction for d.
            # After that i have the correct angle
            for axis in range(2):
                if abs(d[axis]) >= screen_resolution[axis] - self.body[i].diameter:
                    if self.body[i - 1].coord[axis] > self.halfScreen[axis]:
                        d[axis] -= screen_resolution[axis]  # left out
                    else:
                        d[axis] += screen_resolution[axis]  # right out

            angle = math.atan2(d[1], d[0])
            angle %= fullCircle
            self.body[i].move(angle)
            self.body[i].handleOutOfScreen()

    def draw(self):
        for circle in self.body[::-1]:
            circle.draw()

    def addBodyPart(self):
        """ add an circle object at the end of the body"""
        coord = self.body[-1].coord

        coord = [
            coord[0] - math.cos(self.angle) * self.distance,
            coord[1] - math.sin(self.angle) * self.distance
        ]

        circle = Circle(coord, self.radius, self.color, self.surface, self.angle, self.speed)
        self.body.append(circle)

    def getHead(self):
        return self.body[0]

    def eat(self, food):
        for i in range(1, food.energy):
            self.addBodyPart()

    def updateSpeed(self, speed):
        for circle in self.body:
            circle.speed = speed
