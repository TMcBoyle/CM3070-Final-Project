""" Side class to for differentiating between white and black turns.
"""
from enum import Enum

class Side(Enum):
    WHITE = 0
    WHITE_DUCK = 1
    BLACK = 2
    BLACK_DUCK = 3

def advance_turn(current: Side):
    return Side((current.value + 1) % len(Side))

def opposing_side(side: Side):
    if side in (side.WHITE, side.WHITE_DUCK):
        return Side.BLACK
    else:
        return Side.WHITE
