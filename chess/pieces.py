""" Piece-specific functions and objects.
"""
from enum import IntEnum
from .sides import Side

SIDE_MASK  = 0x111000
PIECE_MASK = 0x000111

class PieceType(IntEnum):
    """ General piece type enum. Can be converted to a Piece by calculating
        the value | a Side enum.
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
    Piece.EMPTY:    " ",
    Piece.W_PAWN:   "P",
    Piece.W_KNIGHT: "N",
    Piece.W_BISHOP: "B",
    Piece.W_ROOK:   "R",
    Piece.W_QUEEN:  "Q",
    Piece.W_KING:   "K",
    Piece.B_PAWN:   "p",
    Piece.B_KNIGHT: "n",
    Piece.B_BISHOP: "b",
    Piece.B_ROOK:   "r",
    Piece.B_QUEEN:  "q",
    Piece.B_KING:   "k",
    Piece.DUCK:     "@"
}

symbol_lookup = {val: key for key, val in symbols.items()}
