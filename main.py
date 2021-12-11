from collections import deque
from ast import literal_eval as make_tuple

HZID = '═'
VZID = '║'
HEMPTY = '─'
VEMPTY = '│'
MID = '┼'

P1 = 'X'
P2 = 'O'

WIDTH = 20
HEIGHT = 10
Z = 21323123
marks = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Game:
    def __init__(self, width, height, X1, X2, O1, O2, numOdWallsPerUser):

        self.width = width
        self.height = height
        self.x_pos = [X1, X2]
        self.o_pos = [O1, O2]
        self.numOdWallsPerUser = int(numOdWallsPerUser)
        self.v_walls = [[] for _ in range(self.width * 2)]
        self.h_walls = [[] for _ in range(self.height)]

        self.v_walls[0] = [0, 2, 4]
        self.v_walls[1] = [0, 2, 4]
        self.h_walls[0] = [0, 3]

    def interior(self):
        for y in range(self.height):
            v_wall_row = deque(self.v_walls[y])
            # Vert zidovi i igraci
            for x in range(self.width):
                # Igraci
                if (x, y) in self.x_pos:
                    print(P1, end="")
                elif (x, y) in self.o_pos:
                    print(P2, end="")
                else:
                    print(" ", end="")
                # Vert zidovi
                if x < self.width-1:
                    if len(v_wall_row) > 0 and x == v_wall_row[0]:
                        v_wall_row.popleft()
                        print(VZID, end="")
                    else:
                        print(VEMPTY, end="")
            yield
            # Horizontalni zidovi
            skip_next = False
            h_wall_row = deque(self.h_walls[y])
            if y < self.height-1:
                for x in range(self.width):
                    if skip_next:
                        print(HZID, end="")
                        skip_next = False
                    else:
                        if len(h_wall_row) > 0 and x == h_wall_row[0]:
                            h_wall_row.popleft()
                            skip_next = True
                            print(HZID, end="")
                        else:
                            print(HEMPTY, end="")
                    if(x != self.width-1):
                        print(MID, end="")
            yield

    def draw(self):
        interior = self.interior()
        # 12356...H
        # namesta poziciju za 12356...H, tj pomera ga za 3 da se preklopi
        print(" ", end=" ")
        for y in range(self.width):
            print(marks[y], end=" ")  # stampa ══════════════════ za gornji deo
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
            print('═', end="╩")  # stampa ══════════════════ za donji deo
        print('═', end="╝")  # desni cosak
        print()

    def placeHorizontalWall(self, posY, posX):
        if(posX < self.width-1 and posX not in self.h_walls[posY]):
            self.h_walls[posY].append(posX)
            self.h_walls[posY].sort()

    def placeVerticalWall(self, posY, posX):
        if(posY < self.height-1 and posX not in self.v_walls[posY]):
            self.v_walls[posY].append(posX)
            self.v_walls[posY].sort()
            self.v_walls[posY+1].append(posX)
            self.v_walls[posY+1].sort()

    def parseMove():
        inputString = input("")


def makeGame():
    width = int(input('Enter width:'))
    height = int(input('Enter height:'))
    X1x, X1y = make_tuple(input('Enter player X1 coordinates (x, y):'))
    X2x, X2y = make_touple(input('Enter player X2 coordinates (x, y):'))
    O1x, O1y = make_touple(input('Enter player O1 coordinates (x, y):'))
    O2x, O2y = make_touple(input('Enter player O2 coordinates (x, y):'))
    numOdWallsPerUser = input('Enter number of walls per user:')
    return Game(width, height, (X1x-1, X1y-1), (X2x-1, X2y-1), (O1x-1, O1y-1), (O2x-1, O2y-1), numOdWallsPerUser)


# g = makeGame()
g = Game(20, 10, (0, 0), (1, 1), (9, 9), (8, 8), 9)
g.draw()
