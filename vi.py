from collections import deque, namedtuple
# https://stackoverflow.com/questions/9763116/parse-a-tuple-from-a-string
from ast import literal_eval as make_tuple

HZID = '═'
VZID = '║'
HEMPTY = '─'
VEMPTY = '│'
MID = '┼'

P1 = 'X'
P2 = 'O'
START1 = 'x'
START2 = 'o'

marks = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

Point = namedtuple('Point', 'x y')
Point.__add__ = lambda a,b: Point(a.x+b[0], a.y+b[1]) # type: ignore
Point.__sub__ = lambda a,b: Point(a.x-b[0], a.y-b[1]) # type: ignore

def sign(x):
    if x == 0:
        return 0
    return 1 if x > 0 else -1

class Game:
    def __init__(self, width, height, X1, X2, O1, O2, wall_count_per_player, human_player):
        if width > 22:
            raise Exception("Max width is 22.")
        if height > 28:
            raise Exception("Max height is 28.")
        if wall_count_per_player > 18:
            raise Exception("Max wall count per player is 18")
        self.width = width
        self.height = height
        self.x_pos = [Point(*X1), Point(*X2)]
        self.x_start = self.x_pos.copy()
        self.o_pos = [Point(*O1), Point(*O2)]
        self.o_start = self.o_pos.copy()
        self.wall_count = wall_count_per_player * 2
        self.v_walls = [[] for _ in range(self.width)]
        self.h_walls = [[] for _ in range(self.height)]
        self.playing = 'X'
        self.human_player = human_player

    def interior(self):
        for y in range(self.height):
            v_wall_row = deque(self.v_walls[y])
            # Vert zidovi i igraci/startne pozicije
            for x in range(self.width):
                # Igraci i startne pozicije
                if (x, y) in self.x_pos:
                    print(P1, end="")
                elif (x, y) in self.o_pos:
                    print(P2, end="")
                elif (x, y) in self.x_start:
                    print(START1, end="")
                elif (x, y) in self.o_start:
                    print(START2, end="")
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

    def placeWall(self, wallType, posY, posX):
        if wallType == 'P':
            if posX > 0 and posY > 0 and posX < self.height - 1 and posY < self.width - 1:
                if posX < self.width-1 and posX not in self.h_walls[posY]:
                    self.h_walls[posY].append(posX)
                    self.h_walls[posY].sort()
                    return True
        if wallType == 'Z':
            if posX > 0 and posY > 0 and posX < self.height - 1 and posY < self.width - 1:
                if posY < self.height-1 and posX not in self.v_walls[posY]:
                    self.v_walls[posY].append(posX)
                    self.v_walls[posY].sort()
                    self.v_walls[posY+1].append(posX)
                    self.v_walls[posY+1].sort()
                    return True
        return False

    def parseMove(self):
        while True:
            showError = ""
            inputString = input("Player PlayerNumber PositionX PositionY WallColor WX WY: ")
            arrayString = inputString.split()

            #Player
            if (arrayString[0] in ['X', 'O']):
                showError += "Player: " + arrayString[0] + " doesn't exist. Enter (X/O)\n"

            #Piece Number
            if (int(arrayString[1]) in [1, 2]):
                showError += "PieceNumber: " + arrayString[1] + " doesn't exist. Enter (1/2/3/4)\n"

            #Position X
            if (marks.find(arrayString[2]) > self.width or marks.find(arrayString[2]) < 0):
                showError += "PositionX: " + arrayString[2] + " doesn't exist. Enter between 1 and " + str(self.width) + "\n"

            #Position Y
            if (marks.find(arrayString[3]) > self.height or marks.find(arrayString[3]) < 0):
                showError += "PositionY: " + arrayString[3] + " doesn't exist. Enter between 1 and " + str(self.height) + "\n"

            #Wall Color
            if (arrayString[4] in ['Z', 'P']):
                showError += "WallColor: " + arrayString[4] + " doesn't exist. Enter between Z or P\n"

            #WX
            if (marks.find(arrayString[5]) > self.width - 1 or marks.find(arrayString[5]) < 0):
                showError += "WX: " + arrayString[5] + " doesn't exist. Enter between 1 and " + str(self.width) + "\n"

            #WY
            if (marks.find(arrayString[6]) > self.height - 1 or marks.find(arrayString[6]) < 0):
                showError += "WY: " + arrayString[6] + " doesn't exist. Enter between 1 and " + str(self.height) + "\n"

            if (showError == ""):
                return ((arrayString[0], int(arrayString[1])), Point(marks.find(arrayString[2]), marks.find(arrayString[3])), (arrayString[4], Point(marks.find(arrayString[5]), marks.find(arrayString[6]))))
            else:
                print(showError)

    def inBounds(self, pos):
        x, y = pos
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def isMoveValid(self, pos, move):
        # start_* is pos_* minus one in case of negative numbers
        # So we can check left/upper walls instead of right/lower
        # ones respectively
        def horizontalCheck(pos, dx):
            if dx != 0:
                start_x = (pos.x - 1 if sign(dx) == -1
                           else pos.x)
                return all(all(wall != step_x
                               for step_x in range(start_x, start_x+dx, sign(dx)))
                           for wall in self.v_walls[pos.y])
            else:
                return True
        def verticalCheck(pos, dy):
            if dy != 0:
                start_y = (pos.y - 1 if sign(dy) == -1
                           else pos.y)
                return all(all(wall != pos.x and wall+1 != pos.x
                               for wall in self.h_walls[step_y])
                           for step_y in range(start_y, start_y+dy, sign(dy)))
            else:
                return True

        def diagonalCheck(pos, dx, dy):
            return any([horizontalCheck(pos, dx) and verticalCheck(pos + (dx,0), dy),
                        verticalCheck(pos, dy) and horizontalCheck(pos + (0, dy), dx)])

        # Convert to Point if normal tuple was passed, for debugging
        pos = Point(*pos)
        move = Point(*move)
        dx, dy = move

        if not self.inBounds(pos + move):
            return False
        if (pos+move) in self.o_pos + self.x_pos:
            return False

        if move in {(+2, 0), (-2, 0), (0, +2), (0, -2)}:
            return all([horizontalCheck(pos, dx),
                        verticalCheck(pos, dy)])
        elif move in {(+1, +1), (-1, +1), (+1, -1), (-1, -1)}:
            return diagonalCheck(pos, dx, dy)
        else:
            return False

    def movePiece(self, piece, new_position):
        player_pos = self.x_pos if self.playing == 'X' else self.o_pos
        piece_pos = Point(*player_pos[piece])
        new_position = Point(*new_position)

        if self.isMoveValid(piece_pos, new_position-piece_pos):
            player_pos[piece] = new_position
            self.playing = 'O' if self.playing == 'X' else 'X'
            self.draw() # Privremeno
            return True
        else:
            print("Invalid move")
            return False

    def makeMove(self, player_info, pos, wall):
        player, piece = player_info
        pos = Point(*pos)
        wall_type, wall_pos = wall
        wall_pos = Point(*wall_pos)

        if player != self.playing:
            print("Wrong player")
            return False

        if self.movePiece(piece, pos):
            if self.wall_count > 0:
                if g.placeWall(wall_type, *wall_pos):
                    self.wall_count -= 1
                    return True
                else:
                    print("Invalid wall placement.")
                    return False
        else:
            print("Invalid movement position")
            return False

    def isGameFinished(self):
        if any(x_piece in self.o_start for x_piece in self.x_pos):
            return +1
        if any(x_piece in self.o_start for x_piece in self.x_pos):
            return -1
        return 0

def makeGame():
    width = int(input('Enter width:'))
    height = int(input('Enter height:'))
    X1 = make_tuple(input('Enter player X1 coordinates (x, y):'))
    X2 = make_tuple(input('Enter player X2 coordinates (x, y):'))
    O1 = make_tuple(input('Enter player O1 coordinates (x, y):'))
    O2 = make_tuple(input('Enter player O2 coordinates (x, y):'))
    wall_count = int(input('Enter number of walls per user:'))
    player = input('Are you playing as X or O:')
    return Game(width, height, X1-(1,1), X2-(1,1), O1-(1,1), O2-(1,1), wall_count, player)

g = makeGame()
g.draw()
