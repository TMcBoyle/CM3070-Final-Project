""" Side class to for differentiating between white and black turns.
"""
from enum import IntEnum

class Side(IntEnum):
    WHITE = 0
    WHITE_DUCK = 1
    BLACK = 2
    BLACK_DUCK = 3

def next_turn(current: Side):
    """ Returns a Side object for the next side to play.
    """
    return Side((current.value + 1) % len(Side))

def opposing_side(side: Side):
    if side in (side.WHITE, side.WHITE_DUCK):
        return Side.BLACK
    else:
        return Side.WHITE
