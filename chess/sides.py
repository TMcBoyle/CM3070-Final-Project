""" Side class to for differentiating between white and black turns.
"""
from enum import Enum

class Side(Enum):
    WHITE = 0
    BLACK = 1
    DUCK = 2

def alternate(side: Side):
    if side == Side.WHITE:
        return Side.BLACK
    elif side == Side.BLACK:
        return Side.WHITE
    else:
        return Side.DUCK
