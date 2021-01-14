#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:41:55 2020

@author: dustin
"""

import math

from settings import screen_resolution


class Circle:

    def __init__(self, coord, radius, color, surface, angle, speed):
        self.coord = coord
        self.radius = radius
        self.diameter = radius * 2
        self.color = color
        self.surface = surface
        self.angle = angle
        self.speed = speed

    def move(self, newAngle = None):

        if newAngle is not None:
            self.angle = newAngle

        self.coord[0] += math.cos(self.angle) * self.speed
        self.coord[1] += math.sin(self.angle) * self.speed

    def draw(self):
        import pygame
        pygame.draw.circle(self.surface, self.color, (math.floor(self.coord[0]), math.floor(self.coord[1])),
                           self.radius)

    def checkCollision(self, other_circle):
        return self.getDistanceBorder(other_circle) <= 0

    def getDistanceBorder(self, other_circle):
        return self.getDistanceCenter(other_circle) - self.radius - other_circle.radius

    def getDistanceCenter(self, other_circle):
        diffX = self.coord[0] - other_circle.coord[0]
        diffY = self.coord[1] - other_circle.coord[1]
        return math.sqrt(diffX ** 2 + diffY ** 2)

    def handleOutOfScreen(self):
        """ when the circle is out of screen, set it to the opposite side"""
        for axis in range(2):
            if self.coord[axis] > screen_resolution[axis]:
                self.coord[axis] -= screen_resolution[axis]
            elif self.coord[axis] < 0:
                self.coord[axis] += screen_resolution[axis]