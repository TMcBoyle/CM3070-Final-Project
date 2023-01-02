""" Move generation lookups and functions.
"""
from . import consts
from . import squares
from . import utils
from . import pieces
from . import sides

# Move generation
# Precalculated move arrays
# Pawn capture templates
def _generate_pawn_capture_templates():
    white = []
    black = []
    for idx in range(0, 64):
        if idx <= squares.h1 or idx >= squares.a8: # Skipping rank 1 and 8, as no pawns can exist there
            white.append(consts.EMPTY)
            black.append(consts.EMPTY)
            continue
        square = squares.masks[idx]
        white.append(utils.nwest(square) | utils.neast(square))
        black.append(utils.swest(square) | utils.seast(square))
    return { sides.Side.WHITE: white, sides.Side.BLACK: black }
PAWN_CAPTURE_TEMPLATES = _generate_pawn_capture_templates()

# Knight move templates
def _generate_knight_templates():
    result = []
    for idx in range(0, 64):
        square = squares.masks[idx]
        nnw = utils.north(utils.nwest(square))
        nne = utils.north(utils.neast(square))
        nee = utils.neast(utils.east(square))
        see = utils.seast(utils.east(square))
        sse = utils.south(utils.seast(square))
        ssw = utils.south(utils.swest(square))
        sww = utils.swest(utils.west(square))
        nww = utils.nwest(utils.west(square))

        result.append(
              nnw | nne | nee | see \
            | sse | ssw | sww | nww
        )
    return result
KNIGHT_TEMPLATES = _generate_knight_templates()

# King move templates
def _generate_king_templates():
    result = []
    for idx in range(0, 63):
        square = squares.masks[idx]
        result.append(
              utils.north(square) | utils.east(square)  | utils.south(square) | utils.west(square) \
            | utils.neast(square) | utils.nwest(square) | utils.seast(square) | utils.swest(square)
        )
    return result
KING_TEMPLATES = _generate_king_templates()

# Bishop move templates - i.e., possible bishop moves assuming
# an empty board
def _generate_bishop_templates():
    result = []
    for idx in range(0, 63):
        square = squares.masks[idx]
        diagonal = utils.get_diagonal(idx)
        antidiag = utils.get_antidiagonal(idx)
        result.append(
            (diagonal | antidiag) ^ square
        )
    return result
BISHOP_TEMPLATES = _generate_bishop_templates()

# Rook move templates - i.e., possible rook moves assuming
# an empty board
def _generate_rook_templates():
    result = []
    for idx in range(0, 63):
        square = squares.masks[idx]
        file = utils.get_file(idx)
        rank = utils.get_rank(idx)
        result.append(
            (file | rank) ^ square
        )
    return result
ROOK_TEMPLATES = _generate_rook_templates()

# Move class
class Move:
    """ Holds the from/to square indices of a move, 
        promoted piece, and any other relevant information.
    """
    def __init__(self, from_index: int=None, to_index: int=None, algebraic: str=None, promotion: pieces.Piece=None):
        self.from_square = None
        self.to_square = None
        self.from_mask = None
        self.to_mask = None
        self.from_mask_inv = None
        self.to_mask_inv = None
        self.promotion = None

        if from_index and to_index:
            self.from_square = from_index
            self.to_square   = to_index
        elif algebraic:
            self.from_square = squares.labels.index(algebraic[:2])
            self.to_square   = squares.labels.index(algebraic[2:])
        else:
            self.from_square = 0
            self.to_square = 0
        
        self.from_mask = squares.masks[self.from_square]
        self.to_mask = squares.masks[self.to_square]
        self.from_mask_inv = utils.invert(self.from_mask)
        self.to_mask_inv = utils.invert(self.to_mask)
        
        if promotion:
            self.promotion = promotion

    def apply(self, bitboard: int):
        """ Apply this move to the provided bitboard.
        """
        # If the provided bitboard contains the moving piece...
        if bitboard & self.from_mask:
            # ... remove the piece from the bitboard...
            bitboard = bitboard & self.from_mask_inv
            # ... and add it back in the new position...
            bitboard = bitboard | self.to_mask
        # ... otherwise, zero the bit in the new position.
        else:
            bitboard = bitboard & self.to_mask_inv
        return bitboard
    
    def revert(self, bitboard: int):
        """ Revert the effect of this move on the provided bitboard.
        """
        # If the provided bitboard contains the moved piece
        if bitboard & self.to_mask:
            # ... remove the piece from the bitboard...
            bitboard = bitboard & self.to_mask_inv
            # ... and add it back to its original position...
            bitboard = bitboard | self.from_mask
        # ... otherwise, zero the bit in the original position.
        else:
            bitboard = bitboard & self.from_mask_inv
        return bitboard

    def __str__(self):
        return f"{squares.labels[self.from_square]}{squares.labels[self.to_square]}"
