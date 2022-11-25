""" Bitboard config file - starting position and reusable constants.

    We're using little endian rank-file mapping, so the bit at 2^0 refers
    to the square a1 on the board, and 2^63 refers to square h8. This choice
    is relatively arbitrary but is the most intuitive way to organise the
    bitboards.
"""
from enum import Enum

# Square indices for more intuitive array indexing
a1 = 0;  b1 = 1;  c1 =  2; d1 =  3; e1 =  4; f1 =  5; g1 =  6; h1 =  7
a2 = 8;  b2 = 9;  c2 = 10; d2 = 11; e2 = 12; f2 = 13; g2 = 14; h2 = 15
a3 = 16; b3 = 17; c3 = 18; d3 = 19; e3 = 20; f3 = 21; g3 = 22; h3 = 23
a4 = 24; b4 = 25; c4 = 26; d4 = 27; e4 = 28; f4 = 29; g4 = 30; h4 = 31
a5 = 32; b5 = 33; c5 = 34; d5 = 35; e5 = 36; f5 = 37; g5 = 38; h5 = 39
a6 = 40; b6 = 41; c6 = 42; d6 = 43; e6 = 44; f6 = 45; g6 = 46; h6 = 47
a7 = 48; b7 = 49; c7 = 50; d7 = 51; e7 = 52; f7 = 53; g7 = 54; h7 = 55
a8 = 56; b8 = 57; c8 = 58; d8 = 59; e8 = 60; f8 = 61; g8 = 62; h8 = 63
# Square bitboards to save calculating 2**square repeatedly
class Square():
    bits = [2**n for n in range(64)]
    def __class_getitem__(cls, key):
        return cls.bits[key]

class Side(Enum):
    WHITE = 0
    BLACK = 1

# Fixed board constants (e.g., A file, 3rd rank, light squares etc.)
# Miscellaneous
CONST_EMPTY  = 0x0000000000000000
CONST_FILLED = 0xFFFFFFFFFFFFFFFF
CONST_LIGHT  = 0x55aa55aa55aa55aa
CONST_DARK   = 0xaa55aa55aa55aa55
# Ranks
CONST_RANK_1 = 0x00000000000000FF
CONST_RANK_2 = 0x000000000000FF00
CONST_RANK_3 = 0x0000000000FF0000
CONST_RANK_4 = 0x00000000FF000000
CONST_RANK_5 = 0x000000FF00000000
CONST_RANK_6 = 0x0000FF0000000000
CONST_RANK_7 = 0x00FF000000000000
CONST_RANK_8 = 0xFF00000000000000
LOOKUP_RANK = [
    CONST_RANK_1, CONST_RANK_2, CONST_RANK_3, CONST_RANK_4,
    CONST_RANK_5, CONST_RANK_6, CONST_RANK_7, CONST_RANK_8
]
# Files
CONST_FILE_A = 0x0101010101010101
CONST_FILE_B = 0x0202020202020202
CONST_FILE_C = 0x0404040404040404
CONST_FILE_D = 0x0808080808080808
CONST_FILE_E = 0x1010101010101010
CONST_FILE_F = 0x2020202020202020
CONST_FILE_G = 0x4040404040404040
CONST_FILE_H = 0x8080808080808080
LOOKUP_FILE = [
    CONST_FILE_A, CONST_FILE_B, CONST_FILE_C, CONST_FILE_D, 
    CONST_FILE_E, CONST_FILE_F, CONST_FILE_G, CONST_FILE_H
]
# Diagonals
CONST_DIAG_A1H8 = 0x8040201008040201
CONST_DIAG_A8H1 = 0x0102040810204080

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
INIT_WHITE_PIECES  = CONST_FILE_A | CONST_FILE_B
# Black piece starting positions
INIT_BLACK_PAWNS   = 0x00FF000000000000
INIT_BLACK_ROOKS   = 0x8100000000000000
INIT_BLACK_KNIGHTS = 0x4200000000000000
INIT_BLACK_BISHOPS = 0x2400000000000000
INIT_BLACK_QUEENS  = 0x0800000000000000
INIT_BLACK_KING    = 0x1000000000000000
INIT_BLACK_PIECES  = CONST_FILE_G | CONST_FILE_G
# The duck starting position (i.e., empty)
INIT_DUCK = 0x0000000000000000

# Helper functions
def get_rank(idx: int):
    """ Returns a bitboard representing the rank on which
        the provided square index exists.
    """
    return LOOKUP_FILE[idx % 8]

def get_file(idx: int):
    """ Returns a bitboard representing the file on which
        the provided square index exists.
    """
    return LOOKUP_RANK[idx // 8]

def get_diagonal(idx: int):
    """ Returns a bitboard representing the diagonal
        passing through a given square index (on the a1-h8
        axis). Works by shifting the a1h8 diagonal above the
        board, then shifting back down until it overlaps
        with the provided square.
    """
    result = CONST_DIAG_A1H8 << 56
    while result & Square[idx] == 0:
        result = result >> 8
    return result & CONST_FILLED

def get_antidiagonal(idx: int):
    """ Returns a bitboard representing the diagonal
        passing through a given square index (on the a8-h1
        axis). Works by shifting the a8h1 diagonal above the
        board, then shifting back down until it overlaps
        with the provided square.
    """
    result = CONST_DIAG_A8H1 << 56
    while result & Square[idx] == 0:
        result = result >> 8
    return result & CONST_FILLED

def get_squares(board: int):
    """ Returns an array of square indices for all squares in a
        bitboard containing a "1"
    """
    indices = []
    index = 0
    while board > 0:
        if board % 2 == 1:
            indices.append(index)
        index = index + 1
        board = board >> 1

    return indices

# Invert a bitboard
def invert(board: int):
    """ Inverts a bitboard (i.e., changes all ones to zeros
        and vice versa).
    """
    return board ^ CONST_FILLED

# Delta swap function
def delta_swap(board, mask, delta):
    """ Swaps pairs of bits delta spaces apart where the mask
        contains a "1" in the least significant bit of the pair.

        For example:

            delta_swap(0b10010100, 0b01010101, 1)

        Would result in 0b01101000 - every pair in the original
        board is swapped with the bit one space to the left.

        This is unfortunately unintuitive but it enables many other
        operations to be sped up a lot (especially board rotations).

        https://reflectionsonsecurity.wordpress.com/2014/05/11/efficient-bit-permutation-using-delta-swaps/
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating#Diagonal
    """
    temp  = mask  & (board ^ (board >> delta))
    return  board ^ (temp  ^ (temp  << delta))

# Orthogonal Translations. East and West translations remove 
# any bits that would wrap (e.g., from h1 to a2 when shifting 
# east). North translation removes any bits beyond the 64th.
def north(board: int, times=1):
    return (board << (8 * times)) & CONST_FILLED

def east(board: int, times=1):
    result = board
    for _ in range(times):
        result = (result & invert(CONST_FILE_H)) << 1
    return result

def south(board: int, times=1):
    return board >> (8 * times)

def west(board: int, times=1):
    result = board
    for _ in range(times):
        result = (result & invert(CONST_FILE_A)) >> 1
    return result

# Diagonal Translations
def neast(board: int, times=1):
    return north(east(board, times), times)

def nwest(board: int, times=1):
    return north(west(board, times), times)

def seast(board: int, times=1):
    return south(east(board, times), times)
    
def swest(board: int, times=1):
    return south(west(board, times), times)

# Flips, mirrors and rotations
# Adapted from: https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating
# Flip a bitboard
def flip_vertical(board: int):
    """ Flips a bitboard vertically.
    """
    return    (north(board, 7) & CONST_RANK_8) \
            | (north(board, 5) & CONST_RANK_7) \
            | (north(board, 3) & CONST_RANK_6) \
            | (north(board, 1) & CONST_RANK_5) \
            | (south(board, 1) & CONST_RANK_4) \
            | (south(board, 3) & CONST_RANK_3) \
            | (south(board, 5) & CONST_RANK_2) \
            | (south(board, 7) & CONST_RANK_1)

def flip_horizontal(board: int):
    """ Flips a bitboard horizontally.
    """
    return    (west(board, 7) & CONST_FILE_A) \
            | (west(board, 5) & CONST_FILE_B) \
            | (west(board, 3) & CONST_FILE_C) \
            | (west(board, 1) & CONST_FILE_D) \
            | (east(board, 1) & CONST_FILE_E) \
            | (east(board, 3) & CONST_FILE_F) \
            | (east(board, 5) & CONST_FILE_G) \
            | (east(board, 7) & CONST_FILE_H)

def flip_diagonal_a1h8(board: int):
    """ Flips a bitboard about the a1-h8 diagonal. Uses the delta
        swap algorithm to achieve this quickly.
    """
    # Diagonal mask
    mask = south(CONST_DIAG_A1H8)
    
    # Performing the swaps - we can skip the first iteration
    # as the diagonal itself stays the same.
    for n in range(1, 8):
        board = delta_swap(board, mask, 7 * n)
        mask = south(mask)
    
    return board

def flip_diagonal_a8h1(board: int):
    """ Flips a bitboard about the a8-h1 diagonal. Uses the delta
        swap algorithm to achieve this quickly.
    """
    # Diagonal mask
    mask = south(CONST_DIAG_A8H1)
    
    # Performing the swaps - we can skip the first iteration
    # as the diagonal itself stays the same.
    for n in range(1, 8):
        board = delta_swap(board, mask, 9 * n)
        mask = south(mask)

    return board

# Rotating a bitboard - convenience functions using combinations of
# the flips above.
def rotate_90(board: int):
    """ Rotates a bitboard 90 degress clockwise.
    """
    return flip_vertical(flip_diagonal_a1h8(board))

def rotate_180(board: int):
    """ Rotates a bitboard 180 degrees.
    """
    return flip_horizontal(flip_vertical(board))

def rotate_270(board: int):
    """ Rotates a bitboard 270 degress clockwise.
    """
    return flip_vertical(flip_diagonal_a8h1(board))

# Hyperbola Quintessence algorithm - see https://www.chessprogramming.org/Hyperbola_Quintessence
# for details.
def hyperbola_quintessence(occupancy, mask, piece):
    """ Returns a bitboard representing sliding piece moves along a mask, taking
        into account blocking pieces.
    """
    forward = occupancy & mask
    reverse = rotate_180(forward)
    forward = forward - piece * 2
    reverse = reverse - rotate_180(piece) * 2
    forward = forward ^ rotate_180(reverse)
    return forward & mask

# Move generation
# Precalculated move arrays
# Pawn capture templates
def _generate_pawn_capture_templates():
    white = []
    black = []
    for idx in range(0, 64):
        if idx <= h1 or idx >= a8: # Skipping rank 1 and 8, as no pawns can exist there
            white.append(CONST_EMPTY)
            black.append(CONST_EMPTY)
            continue
        square = Square[idx]
        white.append(nwest(square) | neast(square))
        black.append(swest(square) | seast(square))
    return { 'white': white, 'black': black }
LOOKUP_PAWN_CAPTURE_TEMPLATES = _generate_pawn_capture_templates()

# Knight move templates
def _generate_knight_templates():
    result = []
    for idx in range(0, 64):
        square = Square[idx]
        nnw = north(nwest(square))
        nne = north(neast(square))
        nee = neast(east(square))
        see = seast(east(square))
        sse = south(seast(square))
        ssw = south(swest(square))
        sww = swest(west(square))
        nww = nwest(west(square))

        result.append(
              nnw | nne | nee | see \
            | sse | ssw | sww | nww
        )
    return result
LOOKUP_KNIGHT_TEMPLATES = _generate_knight_templates()

# King move templates
def _generate_king_templates():
    result = []
    for idx in range(0, 63):
        square = Square[idx]
        result.append(
              north(square) | east(square)  | south(square) | west(square) \
            | neast(square) | nwest(square) | seast(square) | swest(square)
        )
    return result
LOOKUP_KING_TEMPLATES = _generate_king_templates()

# Bishop move templates - i.e., possible bishop moves assuming
# an empty board
def _generate_bishop_templates():
    result = []
    for idx in range(0, 63):
        square = Square[idx]
        diagonal = get_diagonal(idx)
        antidiag = get_antidiagonal(idx)
        result.append(
            (diagonal | antidiag) ^ square
        )
    return result
LOOKUP_BISHOP_TEMPLATES = _generate_bishop_templates()

# Rook move templates - i.e., possible rook moves assuming
# an empty board
def _generate_rook_templates():
    result = []
    for idx in range(0, 63):
        square = Square[idx]
        file = get_file(idx)
        rank = get_rank(idx)
        result.append(
            (file | rank) ^ square
        )
    return result
LOOKUP_ROOK_TEMPLATES = _generate_rook_templates()

# Utility functions
def pretty_string(bitboard):
    """ Returns the string representation of a bitboard
        (any 64-bit value) in binary as an 8x8 grid. 
    """ 
    s = f"{bitboard:064b}"
    ranks = []
    for n in range(0, len(s), 8):
        ranks.append(f"{s[n:n+8]}"[::-1] + "\n")
    return "".join(ranks).strip()

def pretty_print(bitboard):
    """ Prints a pretty_string representation of a bitboard.
    """
    print(pretty_string(bitboard))
