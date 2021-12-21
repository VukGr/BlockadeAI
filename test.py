from Game import Game, makeGame, DEBUG, marks
from Util import Point
import unittest
from unittest.mock import patch

def createDummyInput(input_list):
    i = 0
    def fakeInput(prompt=''):
        nonlocal i
        val = input_list[i]
        i += 1
        if i >= len(input_list):
            i = 0
        return val

    return fakeInput

class TestGameClass(unittest.TestCase):
    def setUp(self):
        self.g = Game(20, 10, (0, 0), (1, 1), (9, 9), (8, 8), 9, 'X')
        # Technically blocks X1 in, but that's for later
        # Also a vertical wall crossess a horizontal one on 1,1
        self.g.placeWall('Z', (0,0))
        self.g.placeWall('Z', (2,0))
        self.g.placeWall('Z', (4,0))
        self.g.placeWall('Z', (2,self.g.height-2))
        self.g.placeWall('P', (0,0))
        self.g.placeWall('P', (3,0))
        return super().setUp()

    @patch('builtins.input', createDummyInput(['20', '10',
                                               '1 1', '2 2',
                                               'A A', '9 9',
                                               '9', 'X']))
    def test_makeGame(self):
        game = makeGame()
        self.assertEqual(game.width, 20)
        self.assertEqual(game.height, 10)
        if DEBUG:
            self.assertEqual(game.x_pos, [Point(1,1), Point(2,2)])
            self.assertEqual(game.o_pos, [Point(10,10), Point(9,9)])
        else:
            self.assertEqual(game.x_pos, [Point(0,0), Point(1,1)])
            self.assertEqual(game.o_pos, [Point(9,9), Point(8,8)])
        self.assertEqual(game.wall_count, 9*2)
        self.assertEqual(game.human_player, 'X')

    def test_placeWall_BasicBounds(self):
        g = self.g
        # Bounds
        self.assertFalse(g.placeWall('P', (-1, 0)))
        self.assertFalse(g.placeWall('Z', (-1, -1)))
        self.assertFalse(g.placeWall('P', (g.width, 0)))
        self.assertFalse(g.placeWall('Z', (g.width, 0)))
        self.assertFalse(g.placeWall('Z', (0, g.height)))

    def test_placeWall_Cutoff(self):
        g = self.g
        # HWall Cut off
        self.assertFalse(g.placeWall('P', (g.width-1, 0)))
        self.assertTrue(g.placeWall('P', (g.width-2, 0)))
        # VWall Cut off
        self.assertFalse(g.placeWall('Z', (0, g.height-1)))
        self.assertTrue(g.placeWall('Z', (0, g.height-2)))

    def test_placeWall_Overlap(self):
        g = self.g
        # HWall Overlap
        self.assertTrue(g.placeWall('P', (4, 4)))
        self.assertFalse(g.placeWall('P', (3, 4)))
        self.assertFalse(g.placeWall('P', (4, 4)))
        self.assertFalse(g.placeWall('P', (5, 4)))
        # VWall Overlap
        self.assertTrue(g.placeWall('Z', (1, 4)))
        self.assertFalse(g.placeWall('Z', (1, 3)))
        self.assertFalse(g.placeWall('Z', (1, 4)))
        self.assertFalse(g.placeWall('Z', (1, 5)))

    def test_parseMove(self):
        pass

    def test_isMoveValid(self):
        pass

if __name__ == '__main__':
    unittest.main()
