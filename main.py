from collections import deque
#https://stackoverflow.com/questions/9763116/parse-a-tuple-from-a-string
from ast import literal_eval as make_tuple

HZID = '═'
VZID = '║'
HEMPTY = '─'
VEMPTY = '│'
MID = '┼'

P1 = 'X'
P2 = 'O'

marks = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def sign(x):
    if x == 0:
        return 0
    return 1 if x > 0 else -1

#https://stackoverflow.com/questions/497885/python-element-wise-tuple-operations-like-sum
def add_tuple(a, b):
    tuple(map(sum, zip(a, b)))

class Game:
    def __init__(self, width, height, X1, X2, O1, O2, numOdWallsPerUser):
        self.width = width
        self.height = height
        self.x_pos = [X1, X2]
        self.x_start = self.x_pos
        self.o_pos = [O1, O2]
        self.o_start = self.o_pos
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

    def parseMove(self):
        while True:
            showError = ""
            inputString = input("Player PlayerNumber PositionX PositionY WallColor WX WY: ")
            arrayString = inputString.split()

            #Player
            if (arrayString[0] != "O" and arrayString[0] != 'X'):
                showError += "Player: " + arrayString[0] + " doesn't exist. Enter (X/O)\n"

            #Player Number
            if (int(arrayString[1]) > 4 or int(arrayString[1]) <= 0):
                showError += "PlayerNumber: " + arrayString[1] + " doesn't exist. Enter (1/2/3/4)\n"

            #Position X
            if (marks.find(arrayString[2]) > self.width or marks.find(arrayString[2]) <= 0):
                showError += "PositionX: " + arrayString[2] + " doesn't exist. Enter between 1 and " + str(self.width) + "\n"

            #Position Y
            if (marks.find(arrayString[3]) > self.height or marks.find(arrayString[3]) <= 0):
                showError += "PositionY: " + arrayString[3] + " doesn't exist. Enter between 1 and " + str(self.height) + "\n"

            #Wall Color
            if (arrayString[4] != "Z" and arrayString[4] != 'P'):
                showError += "WallColor: " + arrayString[4] + " doesn't exist. Enter between Z or P\n"

            #WX
            if (marks.find(arrayString[5]) > self.width - 1 or marks.find(arrayString[5]) <= 0):
                showError += "WX: " + arrayString[5] + " doesn't exist. Enter between 1 and " + str(self.width) + "\n"

            #WY
            if (marks.find(arrayString[6]) > self.height - 1 or marks.find(arrayString[6]) <= 0):
                showError += "WY: " + arrayString[6] + " doesn't exist. Enter between 1 and " + str(self.height) + "\n"

            if (showError == ""):
                check = False
                return ((arrayString[0], int(arrayString[1])), (marks.find(arrayString[2]), marks.find(arrayString[3])), (arrayString[4], marks.find(arrayString[5]), marks.find(arrayString[6])))
            else:
                print(showError)

    def in_bounds(self, pos):
        x, y = pos
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def is_move_valid(self, pos, move):
        x, y = pos
        dx, dy = move
        sign_x, sign_y = sign(dx), sign(dy)

        if not self.in_bounds((x+dx, y+dy)):
            return False

        if sign(dx) == -1:
            x -= 1
        if sign(dy) == -1:
            y -= 1

        if move in [(+2, 0), (-2, 0)]:
            return all([wall != x and wall != x + (1*sign_x) for wall in self.v_walls[y]])
        elif move in [(0, +2), (0, -2)]:
            return all([wall != x and wall+1 != x for wall in self.h_walls[y]] +
                       [wall != x and wall+1 != x for wall in self.h_walls[y+(1*sign_y)]])
        elif move in [(+1, +1), (-1, +1), (+1, -1), (-1, -1)]:
            pass
        return False

    def make_move(self, move):
        pass


def makeGame():
    width = int(input('Enter width:'))
    height = int(input('Enter height:'))
    X1x, X1y = make_tuple(input('Enter player X1 coordinates (x, y):'))
    X2x, X2y = make_tuple(input('Enter player X2 coordinates (x, y):'))
    O1x, O1y = make_tuple(input('Enter player O1 coordinates (x, y):'))
    O2x, O2y = make_tuple(input('Enter player O2 coordinates (x, y):'))
    numOdWallsPerUser = input('Enter number of walls per user:')
    return Game(width, height, (X1x-1, X1y-1), (X2x-1, X2y-1), (O1x-1, O1y-1), (O2x-1, O2y-1), numOdWallsPerUser)

#g = makeGame()
g = Game(20, 10, (0, 0), (1, 1), (9, 9), (8, 8), 9)
g.draw()
#print(g.parseMove())
