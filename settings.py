debug = False
#debug = True

screen_resolution = (1200, 800)
fps = 70
maxNumberOfFood = 5
spawnDistanceToBorder = 200

#startup worm:
worm = {
    'speed': 2,
    'radius': 10,
    'length': 10,
    'turnAngle': 0.05
}

food = {
    'speed': 1
}

multiplayer_colors = [
    (0, 0, 255),
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
    (50, 100, 50),
    (255, 0, 100),
    (180, 200, 0),
    (120, 30, 120)
]

multiplayer_max_players = len(multiplayer_colors)

if debug:
    worm['speed'] = 2
    worm['turnAngle'] = 0.3
    fps = 10
    wormSpeed = 2
