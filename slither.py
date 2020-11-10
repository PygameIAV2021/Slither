import pygame
import sys
import random
import math
from worm import Worm

screen_resolution = (500, 500)

def main():
    pygame.init()
    pygame.font.init()
    
    font = pygame.font.SysFont('default', 20)
    
    pygame.display.set_caption('Slither')

    clock = pygame.time.Clock()

    # ini window and returns a surface object
    screen = pygame.display.set_mode(screen_resolution, 0, 32)

    #surface object
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    
    mainWorm = Worm(name="player1", coords=[100,100], color=(0,0,0), surface=screen)

    while (True):
                
        #max fps
        clock.tick(60)
        screen.fill((255,255,255))
        
        
        fpsText = font.render('FPS: ' + str(math.floor(clock.get_fps())) , False, (0,0,0))
        screen.blit(fpsText, (0,0))
        
        mainWorm.move()
        mainWorm.draw()
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
    
main()
