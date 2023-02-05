""" Move generation lookups and functions.
"""
from . import consts
from . import squares
from . import utils
from . import pieces
from . import sides

from enum import Enum

# Castling rights enum
class Castling(Enum):
    WHITE_KINGSIDE = 0
    WHITE_QUEENSIDE = 1
    BLACK_KINGSIDE = 0
    BLACK_QUEENSIDE = 1

# Move types enum
class MoveType(Enum):
    PAWN_SINGLE = 0
    PAWN_DOUBLE = 1
    PAWN_CAPTURE = 2
    PAWN_PROMOTION = 3
    PAWN_CAPTURE_PROMOTION = 4
    KNIGHT = 5
    BISHOP = 6
    ROOK = 7
    QUEEN = 8
    KING = 9
    CASTLE_KINGSIDE = 10
    CASTLE_QUEENSIDE = 11
    DUCK = 12

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
        self.algebraic = None
        self.from_square = None
        self.to_square = None
        self.from_mask = None
        self.to_mask = None
        self.from_mask_inv = None
        self.to_mask_inv = None
        self.move_type = move_type
        self.promotion = promotion

        if algebraic:
            self.algebraic = algebraic
            if algebraic.startswith("@"):
                self.from_square = None
                self.to_square = squares.labels.index(algebraic[1:])
            else:
                self.from_square = squares.labels.index(algebraic[:2])
                self.to_square   = squares.labels.index(algebraic[2:])
        else:
            self.from_square = from_index
            self.to_square = to_index
            if move_type == MoveType.DUCK:
                self.algebraic = f"@{squares.labels[to_index]}"
            elif move_type == MoveType.CASTLE_KINGSIDE:
                self.algebraic = "O-O"
            elif move_type == MoveType.CASTLE_QUEENSIDE:
                self.algebraic = "O-O-O"
            else:
                self.algebraic = f"{squares.labels[from_index]}{squares.labels[to_index]}"

        if self.from_square is not None:
            self.from_mask = squares.masks[self.from_square]
            self.from_mask_inv = utils.invert(self.from_mask)

        if self.to_square is not None:
            self.to_mask = squares.masks[self.to_square]
            self.to_mask_inv = utils.invert(self.to_mask)

    def __key(self):
        return (self.from_square, self.to_square)

    def __eq__(self, other: "Move"):
        if isinstance(other, Move):
            return self.__key() == other.__key()
        return NotImplemented
        
    def __str__(self):
        return (
            f"{self.algebraic}"
            f"{'=' + self.promotion.value if self.promotion else ''}"
        )
    
    # Method from https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def __hash__(self):
        return hash(self.__key)

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
    for idx in range(0, 64):
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
    for idx in range(0, 64):
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
    for idx in range(0, 64):
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
                if piece in (pieces.Piece.PAWN, pieces.Piece.DUCK):
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
                    if piece in (pieces.Piece.PAWN, pieces.Piece.DUCK):
                        continue
                    pawn_captures.append(
                        Move(
                            from_index=pawn,
                            to_index=target,
                            move_type=MoveType.PAWN_CAPTURE_PROMOTION,
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
                    from_index=king,
                    to_index=target,
                    move_type=MoveType.KING
                )
            )
    return king_moves

# Castling move generation
def castling(rooks: int, kings: int, occupation: int, rights: int):
    """ Generates valid castles, taking into account castling rights.
    """
    # Return immediately if there are no valid castling moves.
    if rights == consts.EMPTY:
        return []
    
    castle_moves = []
    # Identify the rooks that are allowed to castle.
    valid_rooks = utils.get_squares(rooks & rights)
    # Check for blockers.
    wq_blockers = occupation & consts.CASTLING_WHITE_QUEENSIDE_BLOCKERS
    wk_blockers = occupation & consts.CASTLING_WHITE_KINGSIDE_BLOCKERS
    bq_blockers = occupation & consts.CASTLING_BLACK_QUEENSIDE_BLOCKERS
    bk_blockers = occupation & consts.CASTLING_BLACK_KINGSIDE_BLOCKERS

    for rook in valid_rooks:
        # White queenside castling is allowed.
        if rook == squares.a1 and wq_blockers == consts.EMPTY:
            castle_moves.append(
                Move(move_type=MoveType.CASTLE_QUEENSIDE)
            )
        # White kingside castling is allowed.
        if rook == squares.h1 and wq_blockers == consts.EMPTY:
            castle_moves.append(
                Move(move_type=MoveType.CASTLE_KINGSIDE)
            )
        # Black queenside castling is allowed.
        if rook == squares.a8 and bq_blockers == consts.EMPTY:
            castle_moves.append(
                Move(move_type=MoveType.CASTLE_QUEENSIDE)
            )
        # Black kingside castling is allowed.
        if rook == squares.h8 and bk_blockers == consts.EMPTY:
            castle_moves.append(
                Move(move_type=MoveType.CASTLE_KINGSIDE)
            )
    
    return castle_moves

# Duck move generation
def duck_moves(origin, occupation):
    """ Generates valid duck moves, taking into account its current
        position and board occupation.
    """
    duck_moves = []
    if origin:
        origin = utils.get_squares(origin)[0]
    for target in utils.get_squares(utils.invert(occupation)):
        duck_moves.append(
            Move(
                from_index=origin,
                to_index=target,
                move_type=MoveType.DUCK
            )
        )
    return duck_moves
