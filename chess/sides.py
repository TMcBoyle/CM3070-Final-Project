""" Side class to for differentiating between white and black turns.
"""
from enum import Enum

class Side(Enum):
    WHITE = 0
    BLACK = 1

def advance_turn(side: Side):
    return Side.WHITE if side == Side.BLACK else Side.BLACK
