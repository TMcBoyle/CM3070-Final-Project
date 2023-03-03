""" Piece-specific functions and objects.
"""
from enum import IntEnum
from .sides import Side

PIECE_MASK = 0x00111

class PieceType(IntEnum):
    """ General piece type enum.
    """
    PAWN   = 0x001
    KNIGHT = 0x010
    BISHOP = 0x011
    ROOK   = 0x100
    QUEEN  = 0x101
    KING   = 0x110
    DUCK   = 0x111

class Piece(IntEnum):
    """ Specific piece type enum. The general piece type can be found
        by calculating the value & 0x00111 and reading as a PieceType.
    """
    EMPTY    = 0x00000
    W_PAWN   = 0x00001
    W_KNIGHT = 0x00010
    W_BISHOP = 0x00011
    W_ROOK   = 0x00100
    W_QUEEN  = 0x00101
    W_KING   = 0x00110
    B_PAWN   = 0x10001
    B_KNIGHT = 0x10010
    B_BISHOP = 0x10011
    B_ROOK   = 0x10100
    B_QUEEN  = 0x10101
    B_KING   = 0x10110
    DUCK     = 0x11111

symbols = {
    Side.WHITE: {
        PieceType.PAWN: "P",
        PieceType.KNIGHT: "N",
        PieceType.BISHOP: "B",
        PieceType.ROOK: "R",
        PieceType.QUEEN: "Q",
        PieceType.KING: "K"
    },
    Side.BLACK: {
        PieceType.PAWN: "p",
        PieceType.KNIGHT: "n",
        PieceType.BISHOP: "b",
        PieceType.ROOK: "r",
        PieceType.QUEEN: "q",
        PieceType.KING: "k"
    },
    PieceType.DUCK: "@"
}

symbol_lookup = {
    "P": (Side.WHITE, PieceType.PAWN),
    "N": (Side.WHITE, PieceType.KNIGHT),
    "B": (Side.WHITE, PieceType.BISHOP),
    "R": (Side.WHITE, PieceType.ROOK),
    "Q": (Side.WHITE, PieceType.QUEEN),
    "K": (Side.WHITE, PieceType.KING),
    "p": (Side.BLACK, PieceType.PAWN),
    "n": (Side.BLACK, PieceType.KNIGHT),
    "b": (Side.BLACK, PieceType.BISHOP),
    "r": (Side.BLACK, PieceType.ROOK),
    "q": (Side.BLACK, PieceType.QUEEN),
    "k": (Side.BLACK, PieceType.KING),
    "@": (None, PieceType.DUCK)
}
