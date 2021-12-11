from collections import deque

class Field:
    arr = []
    pos = None

    x  = None
    y = None

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        pass

    def __repr__(self):
        return f"{(self.x, self.y)})"

num_rows = 11
num_cols = 14

def is_valid(x,y):
    return x >= 0 and y >= 0 and x < num_rows and y < num_cols

def gen_moves(mat, x, y):
    return [mat[y+dy][x+dx]
            for dx in [-1, 0, +1]
            for dy in [-1, 0, +1]
            if is_valid(x+dx, y+dy) and (not ((dx == 0) and (dy == 0)))]

mat = [[Field(row, col) for row in range(num_rows)] for col in range(num_cols)]
for y in range(num_cols):
    for x in range(num_rows):
        mat[y][x].arr = gen_moves(mat,x,y)

#print([(p.x, p.y) for p in mat[2][2].arr])
