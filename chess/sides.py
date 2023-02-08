""" Side class to for differentiating between white and black turns.
"""
from enum import Enum

class Side:
    WHITE = 0
    WHITE_DUCK = 1
    BLACK = 2
    BLACK_DUCK = 3

def advance_turn(current: Side, skip_duck=False):
    if not skip_duck:
        return Side((current + 1) % len(Side))
    else:
        if current in (Side.WHITE, Side.WHITE_DUCK):
            return Side.BLACK
        else:
            return Side.WHITE
