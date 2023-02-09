""" Piece-specific functions and objects.
"""
from enum import Enum
from .sides import Side

class Piece(Enum):
    PAWN = "P"
    KNIGHT = "N"
    BISHOP = "B"
    ROOK = "R"
    QUEEN = "Q"
    KING = "K"
    DUCK = "@"

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
    "N": (Side.WHITE, Piece.PAWN),
    "B": (Side.WHITE, Piece.PAWN),
    "R": (Side.WHITE, Piece.PAWN),
    "Q": (Side.WHITE, Piece.PAWN),
    "K": (Side.WHITE, Piece.PAWN),
    "p": (Side.WHITE, Piece.PAWN),
    "n": (Side.WHITE, Piece.PAWN),
    "b": (Side.WHITE, Piece.PAWN),
    "r": (Side.WHITE, Piece.PAWN),
    "q": (Side.WHITE, Piece.PAWN),
    "k": (Side.WHITE, Piece.PAWN),
    "@": (None, Piece.DUCK),
}
