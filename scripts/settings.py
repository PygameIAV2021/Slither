# This is the setting file. Should be similar on the client- and server-side

debug = False
#debug = True

screen_resolution = (1500, 1000)
fps = 30
maxNumberOfFood = 10
spawnDistanceToBorder = 200

# startup worm:
defaultWorm = {
    'speed': 6,
    'max_speed': 8,
    'min_speed': 1,
    'radius': 10,
    'max_radius': 30,
    'min_radius': 4,
    'length': 10,
    'turnAngle': 0.1,
    'ownHeadColor': (0, 0, 255),
    'enemyHeadColor': (255, 0, 0)
}

food_type_factors = {
    'faster': 0.4,
    'slower': -0.6,
    'bigger': 0.5,
    'smaller': -0.5,
    'count': 4
}

food = {
    'speed': 2
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

#multiplayer_max_players = len(multiplayer_colors)
multiplayer_max_players = 4

if debug:
    screen_resolution = (1000, 800)
    defaultWorm['speed'] = 2
    defaultWorm['turnAngle'] = 0.3
    fps = 1
    wormSpeed = 2
