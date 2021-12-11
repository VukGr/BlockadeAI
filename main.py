from collections import deque

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
    def __init__(self, ) -> None:
        pass
    v_walls = []
    h_walls = []

    x_pos = {(0, 0), (1, 1)}
    o_pos = {(10, 10), (8, 8)}

    def __init__(self, w, h):
        self.v_walls = [[] for _ in range(w * 2)]
        self.h_walls = [[] for _ in range(h)]

        self.v_walls[0] = [0, 2, 4]
        self.v_walls[1] = [0, 2, 4]
        self.h_walls[0] = [0, 3]
        pass

    def interior(self):
        for y in range(HEIGHT):
            v_wall_row = deque(self.v_walls[y])
            # Vert zidovi i igraci
            for x in range(WIDTH):
                # Igraci
                if (x, y) in self.x_pos:
                    print(P1, end="")
                elif (x, y) in self.o_pos:
                    print(P2, end="")
                else:
                    print(" ", end="")
                # Vert zidovi
                if x < WIDTH-1:
                    if len(v_wall_row) > 0 and x == v_wall_row[0]:
                        v_wall_row.popleft()
                        print(VZID, end="")
                    else:
                        print(VEMPTY, end="")
            yield
            # Horizontalni zidovi
            skip_next = False
            h_wall_row = deque(self.h_walls[y])
            if y < HEIGHT-1:
                for x in range(WIDTH):
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
                    if(x != WIDTH-1):
                        print(MID, end="")
            yield

    def draw(self):
        interior = self.interior()
        # 12356...H
        # namesta poziciju za 12356...H, tj pomera ga za 3 da se preklopi
        print(" ", end=" ")
        for y in range(WIDTH):
            print(marks[y], end=" ")  # stampa ══════════════════ za gornji deo
        print()  # prelazak u newline zbog ovo iznad

        # ╔══╗
        print(" ╔", end="")  # levi cosak
        for y in range(WIDTH-1):
            print('═', end="╦")
        print("═", end="╗")  # desni cosak

        # 12356...H + ║ + matrica + ║
        pom = 0
        for x in range(HEIGHT*2-1):
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
        for y in range(WIDTH-1):
            print('═', end="╩")  # stampa ══════════════════ za donji deo
        print('═', end="╝")  # desni cosak
        print()

    def placeHorizontalWall(self, posY, posX):
        if(posX < WIDTH-1 and posX not in self.h_walls[posY]):
            self.h_walls[posY].append(posX)
            self.h_walls[posY].sort()

    def placeVerticalWall(self, posY, posX):
        if(posY < HEIGHT-1 and posX not in self.v_walls[posY]):
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
            if (marks.find(arrayString[2]) > WIDTH or marks.find(arrayString[2]) <= 0):
                showError += "PositionX: " + arrayString[2] + " doesn't exist. Enter between 1 and " + str(WIDTH) + "\n"
            
            #Position Y
            if (marks.find(arrayString[3]) > HEIGHT or marks.find(arrayString[3]) <= 0):
                showError += "PositionY: " + arrayString[3] + " doesn't exist. Enter between 1 and " + str(HEIGHT) + "\n"
            
            #Wall Color
            if (arrayString[4] != "Z" and arrayString[4] != 'P'):
                showError += "WallColor: " + arrayString[4] + " doesn't exist. Enter between Z or P\n"

            #WX
            if (marks.find(arrayString[5]) > WIDTH - 1 or marks.find(arrayString[5]) <= 0):
                showError += "WX: " + arrayString[5] + " doesn't exist. Enter between 1 and " + str(WIDTH) + "\n"

            #WY
            if (marks.find(arrayString[6]) > HEIGHT - 1 or marks.find(arrayString[6]) <= 0):
                showError += "WY: " + arrayString[6] + " doesn't exist. Enter between 1 and " + str(HEIGHT) + "\n"

            if (showError == ""):
                check = False
                return ((arrayString[0], int(arrayString[1])), (marks.find(arrayString[2]), marks.find(arrayString[3])), (arrayString[4], marks.find(arrayString[5]), marks.find(arrayString[6])))
            else:
                print(showError)

g = Game(WIDTH, HEIGHT)
g.draw()
print(g.parseMove())
