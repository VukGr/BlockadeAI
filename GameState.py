from collections import deque
from Util import Point, sign
from Game import marks

# Temporary, hehe
def allMoves():
    return [(+2,0),(-2,0),(0,+2),(0,-2),
            (+1,+1),(-1,+1),(-1,-1),(+1,-1)]

def straightMoves():
    return [Point(+2,0),Point(-2,0),Point(0,+2),Point(0,-2)]

def diagonalMoves():
    return [Point(+1,+1),Point(-1,+1),Point(-1,-1),Point(+1,-1)]

def halfMoves():
    return [Point(+1,0),Point(-1,0),Point(0,+1),Point(0,-1)]

def pointToStr(p):
    return f"({marks[p.x]},{marks[p.y]})"

class GameNode:
    def __init__(self, pos, moves=[]):
        self.pos = Point(*pos)
        self.moves = moves

    def __repr__(self):
        return f"Node(pos={pointToStr(self.pos)}, moves={[(m.x,m.y) for m in self.moves]})"

class GameState:
    def __init__(self, width, height, x_pos, o_pos, human_player):
        # Samo se koristi ako je prazan state!
        # tj nema zidova
        def genMoves(src):
            return ([move if src+move not in self.x_pos + self.o_pos
                     else Point(move.x//2, move.y//2)
                     for move in straightMoves()
                     if self.inBounds(src+move)] +
                    [move for move in diagonalMoves()
                     if self.inBounds(src+move)
                     and src+move not in self.x_pos + self.o_pos])

        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.o_pos = o_pos
        self.v_walls = [[] for _ in range(self.width)]
        self.h_walls = [[] for _ in range(self.height)]
        self.playing = 'X'
        self.human_player = human_player
        self.graph = [[GameNode(Point(x, y), genMoves(Point(x,y)))
                       for x in range(width)]
                      for y in range(height)]

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
            return any([horizontalCheck(pos, dx) and verticalCheck(pos + (dx, 0), dy),
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

    def placeWall(self, wallType, pos):
        # Maybe mergable, *just* swap x and y
        def hRemovePaths(pos):
            # Straight up/down affected for y-1,y,y+1,y+2 for x, x+1
            for y in [pos.y-1, pos.y, pos.y+1, pos.y+2]:
                for x in [pos.x, pos.x+1]:
                    if self.inBounds((x,y)):
                        invalidMoves = {(0,+2),(0,+1)} if y <= pos.y else {(0,-2),(0,-1)}
                        self.graph[y][x].moves = [
                            move for move in self.graph[y][x].moves
                            if move not in invalidMoves]
            # Diagonal affected for y,y+1 for x-1, x, x+1, x+2
            for y in [pos.y, pos.y+1]:
                for x in [pos.x-1, pos.x, pos.x+1, pos.x+2]:
                    if self.inBounds((x,y)):
                        invalidMoves = {move for move in diagonalMoves()
                                       if not self.isMoveValid((x,y), move)}
                        self.graph[y][x].moves = [
                            move for move in self.graph[y][x].moves
                            if move not in invalidMoves]
        def vRemovePaths(pos):
            # Straight left/right affected for x-1,x,x+1,x+2 for y, y+1
            for x in [pos.x-1, pos.x, pos.x+1, pos.x+2]:
                for y in [pos.y, pos.y+1]:
                    if self.inBounds((x,y)):
                        invalidMoves = {(+2,0),(+1,0)} if x <= pos.x else {(-2,0),(-1,0)}
                        self.graph[y][x].moves = [
                            move for move in self.graph[y][x].moves
                            if move != invalidMoves]
            # Diagonal affected for x,x+1 for y-1, y, y+1, y+2
            for x in [pos.x, pos.x+1]:
                for y in [pos.y-1, pos.y, pos.y+1, pos.y+2]:
                    if self.inBounds((x,y)):
                        invalidMoves = {move for move in diagonalMoves()
                                       if not self.isMoveValid((x,y), move)}
                        self.graph[y][x].moves = [
                            move for move in self.graph[y][x].moves
                            if move not in invalidMoves]

        pos = Point(*pos)
        if not self.inBounds(pos):
            return False
        # Horizontal
        if wallType == 'P':
            if pos.x <= self.width-2:
                if all(pos.x+dx not in self.h_walls[pos.y] for dx in [-1, 0, 1]):
                    self.h_walls[pos.y].append(pos.x)
                    self.h_walls[pos.y].sort()
                    hRemovePaths(pos)
                    return True
        # Vertical
        if wallType == 'Z':
            if pos.y <= self.height-2:
                if all(pos.x not in self.v_walls[pos.y + dy] for dy in [-1, 0, 1]):
                    self.v_walls[pos.y].append(pos.x)
                    self.v_walls[pos.y].sort()
                    self.v_walls[pos.y+1].append(pos.x)
                    self.v_walls[pos.y+1].sort()
                    vRemovePaths(pos)
                    return True
        return False

    def movePiece(self, piece, new_position):
        def fixNewSpace(src):
            # Replace straight moves with half ones
            nodes = [src+m for m in straightMoves() if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                halfRel = Point(rel.x//2, rel.y//2)
                self.graph[n.y][n.x].moves = [m for m in self.graph[n.y][n.x].moves
                                              if m != rel]
                self.graph[n.y][n.x].moves.append(halfRel)
            # Remove diagonal moves
            nodes = [src+m for m in diagonalMoves() if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                self.graph[n.y][n.x].moves = [m for m in self.graph[n.y][n.x].moves
                                              if m != rel]

        def fixPrevSpace(src):
            # Replace half moves with proper ones
            nodes = [src+m for m in straightMoves() if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                halfRel = Point(rel.x//2, rel.y//2)
                self.graph[n.y][n.x].moves = [m for m in self.graph[n.y][n.x].moves
                                              if m != halfRel]
                self.graph[n.y][n.x].moves.append(rel)
            # Re-add diagonal moves
            nodes = [src+m for m in diagonalMoves() if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                self.graph[n.y][n.x].moves.append(rel)

        player_pos = self.x_pos if self.playing == 'X' else self.o_pos
        piece_pos = Point(*player_pos[piece])
        new_position = Point(*new_position)
        move = new_position - piece_pos

        if move in self.graph[piece_pos.y][piece_pos.x].moves:
            fixPrevSpace(piece_pos)
            fixNewSpace(new_position)
            player_pos[piece] = new_position
            return True
        else:
            print("Invalid move")
            return False

gs = GameState(50, 50, [(0,0)], [(0,2)], 'X')
