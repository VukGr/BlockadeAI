from Game import makeGame, Game
from pprint import PrettyPrinter

pp = PrettyPrinter()

#g = makeGame()
g = Game(9, 9, (0, 0), (1, 1), (7, 7), (8, 8), 9, 'X')
#gs = GameState(5, 5, [Point(0,0)], [Point(4,4)], 5, 'X')
#g = Game(5,5, (0,0), (1,1), (3,3), (4,4), 5, 'X')

#[g.state.cpuMove() for x in range(100)]
#z = g.state.cpuMove()
#g.play()
