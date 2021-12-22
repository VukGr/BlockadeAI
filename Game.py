from collections import deque
import re
# https://stackoverflow.com/questions/9763116/parse-a-tuple-from-a-string
from ast import literal_eval as make_tuple
from GameState import GameState
from Util import Point, sign
from Config import *

class Game:
    def __init__(self, width, height, X1, X2, O1, O2, wall_count_per_player, human_player):
        if width > 22:
            raise Exception("Max width is 22.")
        if height > 28:
            raise Exception("Max height is 28.")
        if wall_count_per_player > 18:
            raise Exception("Max wall count per player is 18.")
        self.width = width
        self.height = height
        x_pos = [Point(*X1), Point(*X2)]
        o_pos = [Point(*O1), Point(*O2)]
        self.state = GameState(width, height, x_pos, o_pos, wall_count_per_player, human_player)

    def draw(self):
        interior = self.state.drawGen()
        # 12356...H
        # namesta poziciju za 12356...H, tj pomera ga za 3 da se preklopi
        print(" ", end=" ")
        for y in range(self.width):
            print(marks[y], end=" ")  # stampa ═ za gornji deo
        print()  # prelazak u newline zbog ovo iznad

        # ╔══╗
        print(" ╔", end="")  # levi cosak
        for y in range(self.width-1):
            print('═', end="╦")
        print("═", end="╗")  # desni cosak

        # 12356...H + ║ + matrica + ║
        pom = 0
        for x in range(self.height*2-1):
            print()  # spusta u novu liniju jer koristimo svuda end=
            if (x % 2 == 0):
                print(marks[x-pom], end="")
                print('║', end="")
                pom += 1
            else:
                print(' ', end="")
                print('╠', end="")
            next(interior)
            if (x % 2 == 0):
                print('║', end="")
            else:
                print('╣', end="")

        # ╚══╝
        print()  # spusta u novu liniju jer koristimo svuda end=
        print(" ╚", end="")  # levi cosak
        for y in range(self.width-1):
            print('═', end="╩")  # stampa ═ za donji deo
        print('═', end="╝")  # desni cosak
        print()

    def parseMove(self):
        while True:
            inputString = input("Move: ")
            move = [x for x in re.findall(r'\[([^\]]*)\]', inputString)]
            if len(move) != 3:
                print("Invalid move.")
                print("Proper syntax is [Player Piece] [PosX PosY] [WallType WallX WallY].")
                continue
            playerInfo, moveInfo, wallInfo = [ x for x in re.findall(r'\[([^\]]*)\]', inputString)]


            player, piece = playerInfo.split()
            moveX, moveY = moveInfo.split()
            wallType, wallX, wallY = wallInfo.split()

            piece = int(piece)
            movePos = Point(marks.find(moveX), marks.find(moveY))
            wallPos = Point(marks.find(wallX), marks.find(wallY))

            if player not in {'X', 'O'}:
                print(f"Player: {player} doesn't exist. Enter (X/O).")
            elif piece not in {1, 2}:
                print(f"Piece Number: {piece} doesn't exist. Enter (1/2).")
            elif movePos.x not in range(self.width):
                print(f"Position X: {movePos.x} doesn't exist.")
                print(f"Enter between 1 and {marks[self.width-1]}.")
            elif movePos.y not in range(self.height):
                print(f"Position Y: {movePos.y} doesn't exist.")
                print(f"Enter between 1 and {marks[self.height-1]}.")
            elif wallType not in {'Z', 'P'}:
                print(f"Wall Color: {wallType} doesn't exist.")
                print("Enter either Z or P.")
            elif movePos.x not in range(self.width):
                print(f"Wall X: {wallPos.x} doesn't exist.")
                print(f"Enter between 1 and {marks[self.width-1]}.")
            elif movePos.y not in range(self.height):
                print(f"Wall Y: {wallPos.x} doesn't exist.")
                print(f"Enter between 1 and {marks[self.height-1]}.")
            else:
                return ((player, piece-1), movePos, (wallType, wallPos))

    def inBounds(self, pos):
        x, y = pos
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def play(self, cpu=False):
        while not self.state.isGameFinished():
            self.draw()
            if self.state.playing != self.state.human_player and cpu:
                self.state.cpuMove()
            else:
                newState = self.state.makeMove(*self.parseMove())
                if newState != None:
                    self.state = newState

def makeGame():
    def toPoint(string):
        x, y = string.split()
        return Point(marks.find(x),marks.find(y))
    width = int(input('Enter width:'))
    height = int(input('Enter height:'))
    X1 = toPoint(input('Enter player X1 coordinates x y:'))
    X2 = toPoint(input('Enter player X2 coordinates x y:'))
    O1 = toPoint(input('Enter player O1 coordinates x y:'))
    O2 = toPoint(input('Enter player O2 coordinates x y:'))
    wall_count = int(input('Enter number of walls per user:'))
    player = input('Are you playing as X or O:')
    return Game(width, height, X1, X2, O1, O2, wall_count, player)

