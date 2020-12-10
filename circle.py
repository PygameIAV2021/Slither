#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:41:55 2020

@author: dustin
"""

import pygame
import math


class Circle:

    def __init__(self, coord, radius, color, surface):
        self.coord = coord
        self.radius = radius
        self.diameter = radius * 2
        self.color = color
        self.surface = surface

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (math.floor(self.coord[0]), math.floor(self.coord[1])),
                           self.radius)

    def checkCollision(self, other_circle):
        diffX = self.coord[0] - other_circle.coord[0]
        diffY = self.coord[1] - other_circle.coord[1]

        diff = math.sqrt(diffX ** 2 + diffY ** 2)

        return (diff - self.radius - other_circle.radius) <= 0
