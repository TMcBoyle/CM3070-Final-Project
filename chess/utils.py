""" Bitboard utility functions.
"""
from . import squares
from . import consts

import numpy as np
from enum import IntEnum

# Direction Class
class Direction(IntEnum):
    """ Direction enum. Values correspond to the index shift in
        that direction - this assumes the translation is valid (i.e.,
        you aren't trying to shift off the board).
    """
    # Orthogonal
    NORTH =  8
    EAST  =  1
    SOUTH = -8
    WEST  = -1
    # Diagonal
    NEAST = NORTH + EAST
    NWEST = NORTH + WEST
    SEAST = SOUTH + EAST
    SWEST = SOUTH + WEST
    # Extended
    NNEAST = NORTH + NORTH + EAST
    NEEAST = NORTH + EAST  + EAST
    NNWEST = NORTH + NORTH + WEST
    NWWEST = NORTH + WEST  + WEST
    SSEAST = SOUTH + SOUTH + EAST
    SEEAST = SOUTH + EAST  + EAST
    SSWEST = SOUTH + SOUTH + WEST
    SWWEST = SOUTH + WEST  + WEST

# Helper functions
def get_rank(idx: int):
    """ Returns a bitboard representing the rank on which
        the provided square index exists.
    """
    return consts.LOOKUP_RANK[idx // 8]

def get_file(idx: int):
    """ Returns a bitboard representing the file on which
        the provided square index exists.
    """
    return consts.LOOKUP_FILE[idx % 8]

def get_diagonal(idx: int):
    """ Returns a bitboard representing the diagonal
        passing through a given square index (on the a1-h8
        axis). Works by shifting the a1h8 diagonal above the
        board, then shifting back down until it overlaps
        with the provided square.
    """
    result = consts.DIAG_A1H8 << 56
    while result & squares.masks[idx] == 0:
        result = result >> 8
    return result & consts.FILLED

def get_antidiagonal(idx: int):
    """ Returns a bitboard representing the diagonal
        passing through a given square index (on the a8-h1
        axis). Works by shifting the a8h1 diagonal above the
        board, then shifting back down until it overlaps
        with the provided square.
    """
    result = consts.DIAG_A8H1 << 56
    while result & squares.masks[idx] == 0:
        result = result >> 8
    return result & consts.FILLED

def get_squares(board: int):
    """ Returns an array of square indices for all squares in a
        bitboard containing a "1"
    """
    indices = []
    while board > 0:
        indices.append(((board & -board) - 1).bit_count())
        board ^= 2 ** indices[-1]

    return indices

# Invert a bitboard
def invert(board: int):
    """ Inverts a bitboard (i.e., changes all ones to zeros
        and vice versa).
    """
    return board ^ consts.FILLED

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

# Bitboard Translations. East and West translations remove 
# any bits that would wrap (e.g., from h1 to a2 when shifting 
# east). North translation removes any bits beyond the 64th.
def north(board: int, times=1):
    """ Shifts a bitboard north, stripping bits beyond the 64th.
    """
    return (board << (8 * times)) & consts.FILLED

def east(board: int, times=1):
    """ Shifts a bitboard east, preventing wrapping.
    """
    result = board
    for _ in range(times):
        result = (result & consts.EAST_WRAP_MASK) << 1
    return result

def south(board: int, times=1):
    """ Shifts a bitboard south.
    """
    return board >> (8 * times)

def west(board: int, times=1):
    """ Shifts a bitboard west, preventing wrapping.
    """
    result = board
    for _ in range(times):
        result = (result & consts.WEST_WRAP_MASK) >> 1
    return result

# Diagonal Bitboard Translations
def neast(board: int, times=1):
    """ Shifts a bitboard north-east, stripping bits beyond the 64th
        and preventing wrapping.
    """
    return north(east(board, times), times)

def nwest(board: int, times=1):
    """ Shifts a bitboard north-west, stripping bits beyond the 64th
        and preventing wrapping.
    """
    return north(west(board, times), times)

def seast(board: int, times=1):
    """ Shifts a bitboard south-east, preventing wrapping.
    """
    return south(east(board, times), times)
    
def swest(board: int, times=1):
    """ Shifts a bitboard south-west, preventing wrapping.
    """
    return south(west(board, times), times)

def translate(board: int, direction: Direction, times: int=1):
    """ Generalised translation function for ease of use. Calls one
        of the translation functions above based on the direction parameter.
    """
    # Orthogonal Translations
    if direction == Direction.NORTH:
        return north(board, times)
    elif direction == Direction.EAST:
        return east(board, times)
    elif direction == Direction.SOUTH:
        return south(board, times)
    elif direction == Direction.WEST:
        return west(board, times)
    # Diagonal Translations
    elif direction == Direction.NEAST:
        return neast(board, times)
    elif direction == Direction.NWEST:
        return nwest(board, times)
    elif direction == Direction.SEAST:
        return seast(board, times)
    elif direction == Direction.SWEST:
        return swest(board, times)

# Flips, mirrors and rotations
# Adapted from: https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating
# Flip a bitboard
def flip_vertical(board: int):
    """ Flips a bitboard vertically. Adapted from:
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating#Vertical
    """
    k8  = 0x00FF00FF00FF00FF
    k16 = 0x0000FFFF0000FFFF
    board = delta_swap(board, k8, 8)
    board = delta_swap(board, k16, 16)
    board = (board >> 32) | (board << 32)
    return board & consts.FILLED

def flip_horizontal(board: int):
    """ Flips a bitboard horizontally. Adapted from:
        https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating#Horizontal
    """
    k1 = 0x5555555555555555
    k2 = 0x3333333333333333
    k4 = 0x0f0f0f0f0f0f0f0f
    board = delta_swap(board, k1, 1)
    board = delta_swap(board, k2, 2)
    board = delta_swap(board, k4, 4)
    return board & consts.FILLED

def flip_diagonal_a1h8(board: int):
    """ Flips a bitboard about the a1-h8 diagonal. Uses the delta
        swap algorithm to achieve this quickly.
    """
    # Diagonal mask
    mask = south(consts.DIAG_A1H8)
    
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
    mask = south(consts.DIAG_A8H1)
    
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
    reverse = rotate_180(forward & consts.FILLED)
    forward = forward - piece * 2
    reverse = reverse - rotate_180(piece) * 2
    forward = forward ^ rotate_180(reverse & consts.FILLED)
    return forward & mask

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
