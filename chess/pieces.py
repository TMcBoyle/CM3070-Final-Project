""" Piece-specific functions and objects.
"""
from enum import Enum
from .sides import Side

class Piece(Enum):
    PAWN   = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK   = 4
    QUEEN  = 5
    KING   = 6
    DUCK   = 7

symbols = {
    Side.WHITE: {
        Piece.PAWN: "P",
        Piece.KNIGHT: "N",
        Piece.BISHOP: "B",
        Piece.ROOK: "R",
        Piece.QUEEN: "Q",
        Piece.KING: "K"
    },
    Side.BLACK: {
        Piece.PAWN: "p",
        Piece.KNIGHT: "n",
        Piece.BISHOP: "b",
        Piece.ROOK: "r",
        Piece.QUEEN: "q",
        Piece.KING: "k"
    },
    Piece.DUCK: "@"
}

symbol_lookup = {
    "P": (Side.WHITE, Piece.PAWN),
    "N": (Side.WHITE, Piece.KNIGHT),
    "B": (Side.WHITE, Piece.BISHOP),
    "R": (Side.WHITE, Piece.ROOK),
    "Q": (Side.WHITE, Piece.QUEEN),
    "K": (Side.WHITE, Piece.KING),
    "p": (Side.BLACK, Piece.PAWN),
    "n": (Side.BLACK, Piece.KNIGHT),
    "b": (Side.BLACK, Piece.BISHOP),
    "r": (Side.BLACK, Piece.ROOK),
    "q": (Side.BLACK, Piece.QUEEN),
    "k": (Side.BLACK, Piece.KING),
    "@": (None, Piece.DUCK)
}
