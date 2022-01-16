from collections import namedtuple
from Config import *
from functools import lru_cache
from operator import add
import math

Point = namedtuple('Point', 'x y')
Point.__add__ = lru_cache(lambda a, b: Point(a.x+b[0], a.y+b[1]))  # type: ignore
Point.__sub__ = lambda a, b: Point(a.x-b[0], a.y-b[1])  # type: ignore
Point.__mul__ = lambda a, b: Point(a.x*b, a.y*b) #type: ignore
Point.__floordiv__ = lambda a, b: Point(a.x//b, a.y//b) #type: ignore

def pointToStr(p):
    return f"({marks[p.x]},{marks[p.y]})"

def prevToPath(prev_nodes, end):
    path = []
    prev = end
    while prev is not None:
        path.append(prev)
        prev = prev_nodes[prev]
    path.reverse()
    return path

@lru_cache
def pythagora(p1: Point, p2: Point) -> int:
    a = abs(p1.x - p2.x)
    b = abs(p1.y - p2.y)
    return round(math.sqrt(a**2 + b**2))

def sign(x: int):
    if x == 0:
        return 0
    return 1 if x > 0 else -1
