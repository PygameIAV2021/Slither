#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 17:28:45 2020

@author: dustin
"""

from circle import Circle
import math

class Worm ():

    
    def __init__(self, name, coords, surface, color, length = 8, radius=20):
        self.name = name
        
        self.body = []
        self.distance = math.floor(radius / 3)
        self.speed = 1
        self.angle = 0
        
        for i  in range (1, length):
            circle = Circle(coords, radius, (0,0,0), surface)
            self.body.append(circle)            
            coords = [coords[0] + self.distance, coords[1] + self.distance]
            
    def move(self):
        
        self.body[0].coord[0] += math.floor(math.cos(self.angle) * self.speed)
        self.body[0].coord[1] += math.floor(math.sin(self.angle) * self.speed)
            
    def draw(self):
        for circle in self.body:
            circle.draw()
        