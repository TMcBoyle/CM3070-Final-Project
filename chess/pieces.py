""" Piece-specific functions and objects.
"""
from enum import Enum

class Piece(Enum):
    PAWN = "P"
    KNIGHT = "N"
    BISHOP = "B"
    ROOK = "R"
    QUEEN = "Q"
    KING = "K"

symbols = {
    "white": {
        Piece.PAWN: "P",
        Piece.KNIGHT: "N",
        Piece.BISHOP: "B",
        Piece.ROOK: "R",
        Piece.QUEEN: "Q",
        Piece.KING: "K"
    },
    "black": {
        Piece.PAWN: "p",
        Piece.KNIGHT: "n",
        Piece.BISHOP: "b",
        Piece.ROOK: "r",
        Piece.QUEEN: "q",
        Piece.KING: "k"
    }
}
