from collections import namedtuple

Point = namedtuple('Point', 'x y')
Point.__add__ = lambda a, b: Point(a.x+b[0], a.y+b[1])  # type: ignore
Point.__sub__ = lambda a, b: Point(a.x-b[0], a.y-b[1])  # type: ignore

def sign(x: int):
    if x == 0:
        return 0
    return 1 if x > 0 else -1
