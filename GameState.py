from collections import deque
from functools import cache
from Util import Point, sign, pointToStr, prevToPath, pythagora
from Config import *
import math
import pickle
from heapq import heappush, heappop
from pprint import PrettyPrinter

pp = PrettyPrinter()

straightMoves = {Point(+2,0),Point(-2,0),Point(0,+2),Point(0,-2)}
diagonalMoves = {Point(+1,+1),Point(-1,+1),Point(-1,-1),Point(+1,-1)}
halfMoves = {Point(+1,0),Point(-1,0),Point(0,+1),Point(0,-1)}

@cache
def getBestWallType(move):
    return (({(0, 1, 'Z')} if move.x != 0 else set()) |
            ({(1, 0, 'P')} if move.y != 0 else set()))
# Ubaci sve u cache
[getBestWallType(move) for move in straightMoves | diagonalMoves | halfMoves]

class GameNode:
    def __init__(self, pos, moves=[]):
        self.pos = Point(*pos)
        self.moves = moves
    def __repr__(self):
        return f"Node(pos={pointToStr(self.pos)}, moves={[(m.x,m.y) for m in self.moves]})"

class GameState:
    def __init__(self, width, height, x_pos, o_pos, wall_count_per_player, human_player):
        # Samo se koristi ako je prazan state!
        # tj nema zidova
        def genMoves(src):
            return ({move if src+move not in self.x_pos + self.o_pos
                     else move//2
                     for move in straightMoves
                     if self.inBounds(src+move)} |
                    {move for move in diagonalMoves
                     if self.inBounds(src+move)
                     and src+move not in self.x_pos + self.o_pos})

        if width > 22:
            raise Exception("Max width is 22.")
        if height > 28:
            raise Exception("Max height is 28.")
        if wall_count_per_player > 18:
            raise Exception("Max wall count per player is 18.")

        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.o_pos = o_pos
        self.v_walls = [[] for _ in range(self.height)]
        self.x_start = self.x_pos.copy()
        self.h_walls = [[] for _ in range(self.height)]
        self.o_start = self.o_pos.copy()
        self.wall_cross_check = set()
        self.wall_count = wall_count_per_player * 2
        self.playing = 'X'
        self.human_player = human_player
        self.graph = [[GameNode(Point(x, y), genMoves(Point(x,y)))
                       for x in range(width)]
                      for y in range(height)]
        self.calculatePaths()

    def calculatePaths(self):
        self.x_paths = [[self.pathfind(piece, end, False)
                         for piece in self.x_pos]
                        for end in self.o_start]
        self.o_paths = [[self.pathfind(piece, end, False)
                         for piece in self.o_pos]
                        for end in self.x_start]

    def inBounds(self, pos):
        x, y = pos
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def isStateValid(self):
        return all(len(path) != 0
                   for piece in self.x_paths + self.o_paths
                   for path in piece)

    def isMoveValid(self, pos, move, withHalfMove=False):
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
            return ((horizontalCheck(pos, dx) and verticalCheck(pos + (dx, 0), dy)) or
                    (verticalCheck(pos, dy) and horizontalCheck(pos + (0, dy), dx)))

        # Convert to Point if normal tuple was passed, for debugging
        pos = Point(*pos)
        move = Point(*move)
        dx, dy = move

        if not self.inBounds(pos + move):
            return False
        if (pos+move) in self.o_pos + self.x_pos:
            return False

        if move in straightMoves:
            return all([horizontalCheck(pos, dx),
                        verticalCheck(pos, dy)])
        elif move in diagonalMoves:
            return diagonalCheck(pos, dx, dy)
        elif withHalfMove and move in halfMoves:
            return all([horizontalCheck(pos, dx),
                        verticalCheck(pos, dy)])
        else:
            return False

    def isWallValid(self, wallType, pos):
        pos = Point(*pos)
        if pos.x >= 0 and pos.x <= self.width-2 and pos.y >= 0 and pos.y <= self.height-2:
            if pos in self.wall_cross_check:
                return False
            if wallType == 'P':
                return all(pos.x+dx not in self.h_walls[pos.y] for dx in [-1, 0, 1])
            if wallType == 'Z':
                return all(pos.x not in self.v_walls[pos.y + dy] for dy in [0, 1])
        return False

    def placeWall(self, wallType, pos):
        # Maybe mergable, *just* swap x and y
        def hRemovePaths(pos):
            # Straight up/down affected for y-1,y,y+1,y+2 for x, x+1
            for y in [pos.y-1, pos.y, pos.y+1, pos.y+2]:
                for x in [pos.x, pos.x+1]:
                    if self.inBounds((x,y)):
                        invalidMoves = {(0,+2),(0,+1)} if y <= pos.y else {(0,-2),(0,-1)}
                        self.graph[y][x].moves -= invalidMoves
            # Diagonal affected for y,y+1 for x-1, x, x+1, x+2
            for y in [pos.y, pos.y+1]:
                for x in [pos.x-1, pos.x, pos.x+1, pos.x+2]:
                    if self.inBounds((x,y)):
                        invalidMoves = {move for move in diagonalMoves
                                        if not self.isMoveValid((x,y), move)}
                        self.graph[y][x].moves -= invalidMoves
        def vRemovePaths(pos):
            # Straight left/right affected for x-1,x,x+1,x+2 for y, y+1
            for x in [pos.x-1, pos.x, pos.x+1, pos.x+2]:
                for y in [pos.y, pos.y+1]:
                    if self.inBounds((x,y)):
                        invalidMoves = {(+2,0),(+1,0)} if x <= pos.x else {(-2,0),(-1,0)}
                        self.graph[y][x].moves -= invalidMoves
            # Diagonal affected for x,x+1 for y-1, y, y+1, y+2
            for x in [pos.x, pos.x+1]:
                for y in [pos.y-1, pos.y, pos.y+1, pos.y+2]:
                    if self.inBounds((x,y)):
                        invalidMoves = {move for move in diagonalMoves
                                        if not self.isMoveValid((x,y), move)}
                        self.graph[y][x].moves -= invalidMoves
        # Not used anymore
        def isWallTouching(pos):
            if wallType == 'P':
                if pos.x == 0 or pos.x == self.width-2:
                    return True
                return any([pos.x-2 in self.h_walls[pos.y],
                            pos.x+2 in self.h_walls[pos.y]] +
                           [pos.x+dx-1 in self.v_walls[pos.y+dy+1]
                            for dx in [0,1,2]
                            for dy in [-1,0]
                            if dy >= 0])
            else:
                if pos.y == 0 or pos.y == self.height-2:
                    return True
                return any([pos.x in self.v_walls[pos.y-1],
                            pos.x in self.v_walls[pos.y+1]] +
                           [pos.x+dx+1 in self.h_walls[pos.y+dy-1]
                            for dx in [-2,-1,0]
                            for dy in [0,1,2]])
        pos = Point(*pos)
        if not self.isWallValid(wallType, pos):
            return False
        # Horizontal
        if wallType == 'P':
            self.h_walls[pos.y].append(pos.x)
            self.h_walls[pos.y].sort()
            self.wall_cross_check.add(pos)
            hRemovePaths(pos)
        # Vertical
        if wallType == 'Z':
            self.v_walls[pos.y].append(pos.x)
            self.v_walls[pos.y].sort()
            self.v_walls[pos.y+1].append(pos.x)
            self.v_walls[pos.y+1].sort()
            self.wall_cross_check.add(pos)
            vRemovePaths(pos)
        # Recalculate paths
        self.calculatePaths()
        if self.isStateValid():
            return True
        else:
            return False

    def movePiece(self, piece, new_position):
        def fixNewSpace(src):
            # Replace straight moves with half ones
            nodes = [src+m for m in straightMoves if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                halfRel = rel // 2
                self.graph[n.y][n.x].moves.discard(rel)
                self.graph[n.y][n.x].moves.add(halfRel)
            # Remove diagonal moves
            nodes = [src+m for m in diagonalMoves if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                self.graph[n.y][n.x].moves.discard(rel)

        def fixPrevSpace(src):
            # Replace half moves with proper ones
            nodes = [src+m for m in straightMoves if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                halfRel = rel // 2
                self.graph[n.y][n.x].moves.add(rel)
                self.graph[n.y][n.x].moves.discard(halfRel)
            # Re-add diagonal moves
            nodes = [src+m for m in diagonalMoves if self.inBounds(src+m)]
            for n in nodes:
                rel = src - n
                self.graph[n.y][n.x].moves.add(rel)

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
            return False

    def doMove(self, player_info, pos, wall, printWarning=True):
        player, piece = player_info
        pos = Point(*pos)
        wall_type, wall_pos = wall
        wall_pos = Point(*wall_pos)

        if player != self.playing:
            if printWarning:
                print("Wrong player")
            return False

        if self.movePiece(piece, pos):
            if self.wall_count > 0:
                if self.placeWall(wall_type, wall_pos):
                    self.wall_count -= 1
                    self.playing = 'O' if self.playing == 'X' else 'X'
                    return True
                else:
                    if printWarning:
                        print("Invalid wall placement.")
                    return False
            else:
                self.playing = 'O' if self.playing == 'X' else 'X'
                return True
        else:
            if printWarning:
                print("Invalid movement position")
            return False

    def makeMove(self, player_info, pos, wall, printWarning=True):
        # https://stackoverflow.com/questions/24756712/deepcopy-is-extremely-slow
        newState = pickle.loads(pickle.dumps(self))
        if newState.doMove(player_info, pos, wall, printWarning):
            return newState
        else:
            return None

    def score(self):
        isDone = self.isGameFinished()
        if isDone != 0:
            return 999999 * isDone

        return (min(len(path) for path in self.o_paths) -
                min(len(path) for path in self.x_paths))

    def cpuMove(self, depth=2, limit=None):
        if self.isGameFinished() != 0:
            return self

        piecePath = self.x_paths if self.playing == 'X' else self.o_paths
        piecePathOpp = self.o_paths if self.playing == 'X' else self.x_paths
        allPieceMoves = [(i, pos)
                         for i,path in enumerate(piecePath)
                         for pos in (p[1] for p in path)]
        allWallMoves = {('Z', Point(0,0))}
        if self.wall_count > 0:
            allWallMoves = {(t, Point(x,y))
                            for piece in piecePathOpp
                            for p in piece
                            for (dx, dy, t) in getBestWallType(p[1]-p[0])
                            for x in range(min(p[0].x, p[1].x) - dx, max(p[0].x, p[1].x) + dx)
                            for y in range(min(p[0].y, p[1].y) - dy, max(p[0].y, p[1].y) + dy)
                            if self.isWallValid(t, Point(x,y))}
        allMoves = [(pieceMove, wallMove)
                    for wallMove in allWallMoves
                    for pieceMove in allPieceMoves]
        minmax = max if self.playing == 'X' else min
        minmaxPrev = min if self.playing == 'X' else max
        worstScore = minmaxPrev(math.inf, -math.inf)
        states = filter(None, (self.makeMove((self.playing, piece), pieceMove, wallMove, False)
                               for (piece, pieceMove), wallMove in allMoves))
        if depth == 1:
            if limit == None:
                return minmax(states, key=(lambda s: s.score()), default=None)
            else:
                bestScore = worstScore
                bestState = None
                for state in states:
                    score = state.score()
                    if minmaxPrev(limit, score) == limit:
                        return None
                    if minmax(bestScore, score) == score:
                        bestScore = score
                        bestState = state
                return bestState
        else:
            bestScore = worstScore
            bestState = None
            for state in states:
                bestChild = state.cpuMove(depth-1, bestScore)
                if bestChild == None:
                    continue
                score = bestChild.score()
                if limit != None and minmaxPrev(limit, score) == limit:
                    return None
                if minmax(bestScore, score) == score:
                    bestScore = score
                    bestState = state
            return bestState

    def isGameFinished(self):
        if any(x_piece in self.o_start for x_piece in self.x_pos):
            return +1
        if any(o_piece in self.x_start for o_piece in self.o_pos):
            return -1
        return 0

    def pathfind(self, start, end, full=True):
        movement_cost = 1
        start = Point(*start)
        end = Point(*end)
        end_adjacents = {end+move for move in self.graph[end.y][end.x].moves}
        end_adjacents |= {end+move for move in halfMoves if self.isMoveValid(end, Point(0,0) - move)}
        open_set = set([start])
        open_heap = [(0, start)]
        closed_set = set()
        g = {start: 0}
        prev_nodes = {start: None}
        while len(open_set) > 0:
            _, node = heappop(open_heap)

            # Found end node
            if full:
                if node == end:
                    return prevToPath(prev_nodes, end)
            elif node in end_adjacents:
                if end not in prev_nodes:
                    prev_nodes[end] = node
                return prevToPath(prev_nodes, end)

            for move in self.graph[node.y][node.x].moves:
                m = node + move
                # First time
                if m not in open_set and m not in closed_set:
                    open_set.add(m)
                    g[m] = g[node] + movement_cost
                    heappush(open_heap, (g[m] + pythagora(m, end), m))
                    prev_nodes[m] = node
                # Update
                elif g[m] > g[node] + movement_cost:
                    g[m] = g[node] + movement_cost
                    prev_nodes[m] = node
                    # Probably unneeded here?
                    if m in closed_set:
                        closed_set.remove(m)
                        open_set.add(m)
                        heappush(open_heap, (g[m] + pythagora(m, end), m))
            open_set.remove(node)
            closed_set.add(node)
        return []

    def drawGen(self):
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
