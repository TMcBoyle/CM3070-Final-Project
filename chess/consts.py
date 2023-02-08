""" Miscellaneous bitboard constants (e.g., A file, starting positions etc.).
"""
from .sides import Side
from .pieces import Piece

# Fixed board constants (e.g., A file, 3rd rank, light squares etc.)
# Miscellaneous
EMPTY  = 0x0000000000000000
FILLED = 0xFFFFFFFFFFFFFFFF
LIGHT  = 0x55aa55aa55aa55aa
DARK   = 0xaa55aa55aa55aa55
# Ranks
RANK_1 = 0x00000000000000FF
RANK_2 = 0x000000000000FF00
RANK_3 = 0x0000000000FF0000
RANK_4 = 0x00000000FF000000
RANK_5 = 0x000000FF00000000
RANK_6 = 0x0000FF0000000000
RANK_7 = 0x00FF000000000000
RANK_8 = 0xFF00000000000000
LOOKUP_RANK = [
    RANK_1, RANK_2, RANK_3, RANK_4,
    RANK_5, RANK_6, RANK_7, RANK_8
]
# Files
FILE_A = 0x0101010101010101
FILE_B = 0x0202020202020202
FILE_C = 0x0404040404040404
FILE_D = 0x0808080808080808
FILE_E = 0x1010101010101010
FILE_F = 0x2020202020202020
FILE_G = 0x4040404040404040
FILE_H = 0x8080808080808080
LOOKUP_FILE = [
    FILE_A, FILE_B, FILE_C, FILE_D, 
    FILE_E, FILE_F, FILE_G, FILE_H
]
# Diagonals
DIAG_A1H8 = 0x8040201008040201
DIAG_A8H1 = 0x0102040810204080
# Sample boards for test functions
TEST_R_SHAPE     = 0x1E2222120E0A1222
TEST_UPPER_RIGHT = 0xFFFEFCF8F0E0C080
TEST_UPPER_LEFT  = 0xFF7F3F1F0F070301

# Starting positions
# Brief explanation of the concept - for the starting position of white's 
# pawns, the occupied squares should be:
#
# h | 0 0 0 0 0 0 0 0
# g | 0 0 0 0 0 0 0 0
# f | 0 0 0 0 0 0 0 0
# e | 0 0 0 0 0 0 0 0
# d | 0 0 0 0 0 0 0 0
# c | 0 0 0 0 0 0 0 0
# b | 1 1 1 1 1 1 1 1 
# a | 0 0 0 0 0 0 0 0
#   L-----------------
#     1 2 3 4 5 6 7 8
#
# Converting this to a 64-bit integer with a1 as the first bit gives:
# 0b0000000000000000000000000000000000000000000000001111111100000000
#
# Or, converted to hexadecimal for brevity:
# 0x000000000000FF00)
#
# More detailed information can be found at https://www.chessprogramming.org/Bitboards
#
# White piece starting positions
INIT_WHITE_PAWNS   = 0x000000000000FF00
INIT_WHITE_ROOKS   = 0x0000000000000081
INIT_WHITE_KNIGHTS = 0x0000000000000042
INIT_WHITE_BISHOPS = 0x0000000000000024
INIT_WHITE_QUEENS  = 0x0000000000000008
INIT_WHITE_KING    = 0x0000000000000010
INIT_WHITE_PIECES  = RANK_1 | RANK_2
# Black piece starting positions
INIT_BLACK_PAWNS   = 0x00FF000000000000
INIT_BLACK_ROOKS   = 0x8100000000000000
INIT_BLACK_KNIGHTS = 0x4200000000000000
INIT_BLACK_BISHOPS = 0x2400000000000000
INIT_BLACK_QUEENS  = 0x0800000000000000
INIT_BLACK_KING    = 0x1000000000000000
INIT_BLACK_PIECES  = RANK_7 | RANK_8
# The duck starting position (i.e., empty)
INIT_DUCK = 0x0000000000000000
# Starting occupation mask
INIT_ALL_PIECES = INIT_WHITE_PIECES | INIT_BLACK_PIECES | INIT_DUCK

# Castling masks
# Kingside
CASTLING_KINGSIDE = {
    Side.WHITE: {
        "BLOCKERS": (FILE_F | FILE_G) & RANK_1,
        Piece.KING:     (FILE_E | FILE_G) & RANK_1,
        Piece.ROOK:     (FILE_F | FILE_H) & RANK_1
    },
    Side.BLACK: {
        "BLOCKERS": (FILE_F | FILE_G) & RANK_8,
        Piece.KING: (FILE_E | FILE_G) & RANK_8,
        Piece.ROOK: (FILE_F | FILE_H) & RANK_8
    }
}
# Queenside
CASTLING_QUEENSIDE = {
    Side.WHITE: {
        "BLOCKERS": (FILE_B | FILE_C | FILE_D) & RANK_1,
        Piece.KING:     (FILE_E | FILE_C) & RANK_1,
        Piece.ROOK:     (FILE_A | FILE_D) & RANK_1
    },
    Side.BLACK: {
        "BLOCKERS": (FILE_B | FILE_C | FILE_D) & RANK_8,
        Piece.KING: (FILE_E | FILE_C) & RANK_8,
        Piece.ROOK: (FILE_F | FILE_H) & RANK_8
    }
}
