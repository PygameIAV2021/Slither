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
    'turnAngle': 0.01
}

food = {
    'speed': 1
}

if debug:
    worm['speed'] = 2
    worm['turnAngle'] = 0.3
    fps = 10
    wormSpeed = 2
