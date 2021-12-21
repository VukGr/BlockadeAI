from Game import Game, makeGame, DEBUG

#g = makeGame()
g = Game(20, 10, (0, 0), (1, 1), (9, 9), (8, 8), 9, 'X')

# Z - Verical
# P - Horizontal
if DEBUG:
    g.placeWall('Z', (0,0))
    g.placeWall('Z', (2,0))
    g.placeWall('Z', (4,0))
    g.placeWall('Z', (2,g.height-3))
    g.placeWall('P', (0,0))
    g.placeWall('P', (3,0))

g.play()
# print(g.parseMove())
