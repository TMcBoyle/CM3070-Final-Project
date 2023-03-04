""" Side class to for differentiating between white and black turns.
"""
from enum import IntEnum

class Side(IntEnum):
    WHITE      = 0x000000
    WHITE_DUCK = 0x001000
    BLACK      = 0x010000
    BLACK_DUCK = 0x011000

def next_turn(current: Side):
    """ Returns a Side object for the next side to play.
    """
    return \
             Side.WHITE      if current == Side.BLACK_DUCK \
        else Side.WHITE_DUCK if current == Side.WHITE      \
        else Side.BLACK      if current == Side.WHITE_DUCK \
        else Side.BLACK_DUCK

def opposing_side(side: Side):
    if side in (side.WHITE, side.WHITE_DUCK):
        return Side.BLACK
    else:
        return Side.WHITE
