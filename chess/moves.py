""" Move generation lookups and functions.
"""
from . import consts
from . import squares
from . import utils
from . import pieces
from . import sides

# Castling rights enum
class Castling:
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 0
    BLACK_QUEENSIDE = 1

# Move types enum
class MoveType:
    PAWN_SINGLE = 0
    PAWN_DOUBLE = 1
    PAWN_CAPTURE = 2
    PAWN_PROMOTION = 3
    KNIGHT = 4
    BISHOP = 5
    ROOK = 6
    QUEEN = 7
    KING = 8
    CASTLE_KINGSIDE = 9
    CASTLE_QUEENSIDE = 10

# Move class
class Move:
    """ Holds the from/to square indices of a move, 
        promoted piece, and any other relevant information.
    """
    def __init__(
            self, 
            algebraic: str=None,
            from_index: int=None,
            to_index: int=None,
            move_type: MoveType=None,
            promotion: pieces.Piece=None
        ):
        self.from_square = None
        self.to_square = None
        self.from_mask = None
        self.to_mask = None
        self.from_mask_inv = None
        self.to_mask_inv = None
        self.move_type = move_type
        self.promotion = promotion

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
        return (
            f"{squares.labels[self.from_square]}"
            f"{squares.labels[self.to_square]}"
            f"{'=' + self.promotion.value if self.promotion else ''}"
        )

# Move template generation
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
              utils.north(square) | utils.east(square)  \
            | utils.south(square) | utils.west(square)  \
            | utils.neast(square) | utils.nwest(square) \
            | utils.seast(square) | utils.swest(square)
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

# Move generation
# Sliding piece move generation (generic)
def sliding_moves(
        origin: int,
        axes: list,
        occupation: int,
        blockers: int,
        move_type: MoveType=None
    ):
    """ Generates valid sliding moves from a given origin square,
        based on the provided occupation and blocker bitboards, along the
        given axis masks.
    """
    # Generate pseudo-legal move templates
    templates = []
    for axis in axes:
        templates.append(utils.hyperbola_quintessence(
            occupation,
            axis,
            squares.masks[origin]
        ))

    # Combine the above templates
    targets = consts.EMPTY
    for template in templates:
        targets = targets | template
    targets = targets & utils.invert(blockers)

    # Build the move objects
    moves = []
    for target in utils.get_squares(targets):
        moves.append(
            Move(
                from_index=origin,
                to_index=target,
                move_type=move_type
            )
        )

    return moves

# Pawn move generation
# Pushes
def pawn_pushes(origins: int, occupation: int, side: sides.Side):
    """ Generates valid pawn moves from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    if side == sides.Side.WHITE:
        direction = utils.Direction.NORTH
        promotion_rank = consts.RANK_8
        single_pushes = utils.north(origins) & utils.invert(occupation)
        double_pushes = \
            (utils.north(single_pushes) & utils.invert(occupation)) & consts.RANK_4
    elif side == sides.Side.BLACK:
        direction = utils.Direction.SOUTH
        promotion_rank = consts.RANK_1
        single_pushes = utils.south(origins) & utils.invert(occupation)
        double_pushes = \
            (utils.south(single_pushes) & utils.invert(occupation)) & consts.RANK_5

    pawn_pushes = []
    # Single pushes and promotions.
    for target in utils.get_squares(single_pushes):
        # Check if the pawn should promote - if so, add possible promotions.
        if squares.masks[target] & promotion_rank:
            for piece in pieces.Piece:
                if piece == pieces.Piece.PAWN:
                    continue
                pawn_pushes.append(
                    Move(
                        from_index=target - direction,
                        to_index=target,
                        move_type=MoveType.PAWN_PROMOTION,
                        promotion=piece
                    )
                )
        # Otherwise add a regular pawn push.
        else:
            pawn_pushes.append(
                Move(
                    from_index=target - direction,
                    to_index=target,
                    move_type=MoveType.PAWN_SINGLE
                )
            )
    # Double pushes - note these can't be promotions.
    for target in utils.get_squares(double_pushes):
        pawn_pushes.append(
            Move(
                from_index=target - direction * 2,
                to_index=target,
                move_type=MoveType.PAWN_DOUBLE
            )
        )
    return pawn_pushes

# Captures
def pawn_captures(origins: int, enemies: int, side: sides.Side):
    """ Generates valid pawn captures from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    if side == sides.Side.WHITE:
        promotion_rank = consts.RANK_8
    elif side == sides.Side.BLACK:
        promotion_rank = consts.RANK_1

    pawn_captures = []
    for pawn in utils.get_squares(origins):
        template = PAWN_CAPTURE_TEMPLATES[side][pawn]
        targets = template & enemies
        for target in utils.get_squares(targets):
            # Check if this capture leads to a promotion.
            if squares.masks[target] & promotion_rank:
                # If so, add possible promotions.
                for piece in pieces.Piece:
                    if piece == pieces.Piece.PAWN:
                        continue
                    pawn_captures.append(
                        Move(
                            from_index=pawn,
                            to_index=target,
                            move_type=MoveType.PAWN_PROMOTION,
                            promotion=piece
                        )
                    )
            # Otherwise, add a normal pawn capture.
            else:
                pawn_captures.append(
                    Move(
                        from_index=pawn,
                        to_index=target,
                        move_type=MoveType.PAWN_CAPTURE
                    )
                )
    return pawn_captures

# Knight move generation
def knight_moves(origins: int, occupation: int, blockers: int):
    """ Generates valid knight moves from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    knight_moves = []
    for knight in utils.get_squares(origins):
        # Get the move template for this knight.
        template = KNIGHT_TEMPLATES[knight]
        targets = template & utils.invert(blockers)
        for target in utils.get_squares(targets):
            knight_moves.append(
                Move(
                    from_index=knight,
                    to_index=target,
                    move_type=MoveType.KNIGHT
                )
            )
    return knight_moves

# Bishop move generation
def bishop_moves(origins: int, occupation: int, blockers: int):
    """ Generates valid bishop moves from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    bishop_moves = []

    for origin in utils.get_squares(origins):
        bishop_moves += sliding_moves(
            origin,
            [
                utils.get_diagonal(origin), 
                utils.get_antidiagonal(origin)
            ],
            occupation,
            blockers,
            MoveType.BISHOP
        )
    return bishop_moves

# Rook move generation
def rook_moves(origins: int, occupation: int, blockers: int):
    """ Generates valid rook moves from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    rook_moves = []

    for origin in utils.get_squares(origins):
        rook_moves += sliding_moves(
            origin,
            [
                utils.get_rank(origin), 
                utils.get_file(origin)
            ],
            occupation,
            blockers,
            MoveType.ROOK
        )
    return rook_moves

# Queen move generation
def queen_moves(origins: int, occupation: int, blockers: int):
    """ Generates valid queen moves from a given set of origin squares,
        taking into account board occupation and blockers.
    """
    queen_moves = []

    for origin in utils.get_squares(origins):
        queen_moves += sliding_moves(
            origin,
            [
                utils.get_rank(origin),
                utils.get_file(origin),
                utils.get_diagonal(origin), 
                utils.get_antidiagonal(origin)
            ],
            occupation,
            blockers,
            MoveType.QUEEN
        )
    return queen_moves

# King move generation
def king_moves(origins: int, occupation: int, blockers: int):
    """ Generates valid knight moves from a given origin square,
        taking into account board occupation and blockers.
    """
    king_moves = []
    for king in utils.get_squares(origins):
        # Get the move template for this king.
        template = KING_TEMPLATES[king]
        targets = template & utils.invert(blockers)
        for target in utils.get_squares(targets):
            king_moves.append(
                Move(
                    from_index = king,
                    to_index=target,
                    move_type=MoveType.KING
                )
            )
    return king_moves
