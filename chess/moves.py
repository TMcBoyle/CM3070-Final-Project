""" Move generation lookups and functions.
"""
from . import consts
from . import squares
from . import utils
from . import pieces
from . import sides

from enum import Enum

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
    def __init__(self, move_type: MoveType, piece: pieces.Piece=None, from_index: int=None, to_index: int=None, promotion: pieces.Piece=None):
        self.move_type = move_type
        self.piece = piece
        self.from_index = from_index
        self.to_index = to_index
        self.promotion = promotion

    def __key(self):
        return (self.from_index, self.to_index, self.move_type, self.promotion)
    
    def __eq__(self, other: "Move"):
        if not isinstance(other, Move):
            return NotImplemented
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"<chess.moves.Move: " \
               f"from_index={self.from_index}, " \
               f"to_index={self.to_index}, " \
               f"move_type={self.move_type}, " \
               f"promotion={self.promotion}>"

    def __str__(self):
        if self.move_type == MoveType.CASTLE_KINGSIDE:
            return "O-O"
        elif self.move_type == MoveType.CASTLE_QUEENSIDE:
            return "O-O-O"
        elif self.move_type == MoveType.DUCK:
            return f"@{squares.labels(self.to_index)}"
        elif self.move_type in (MoveType.PAWN_PROMOTION, MoveType.PAWN_CAPTURE_PROMOTION):
            return f"{squares.labels[self.from_index]}{squares.labels[self.to_index]}={self.promotion}"
        else:
            return f"{squares.labels[self.from_index]}{squares.labels[self.to_index]}"

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
        move_type: MoveType=None,
        piece: pieces.Piece=None
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
                move_type=move_type,
                piece=piece,
                from_index=origin,
                to_index=target
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
                        move_type=MoveType.PAWN_PROMOTION,
                        piece=pieces.Piece.PAWN,
                        from_index=target - direction,
                        to_index=target,
                        promotion=piece
                    )
                )
        # Otherwise add a regular pawn push.
        else:
            pawn_pushes.append(
                Move(
                    move_type=MoveType.PAWN_SINGLE,
                    piece=pieces.Piece.PAWN,
                    from_index=target - direction,
                    to_index=target
                )
            )
    # Double pushes - note these can't be promotions.
    for target in utils.get_squares(double_pushes):
        pawn_pushes.append(
            Move(
                move_type=MoveType.PAWN_DOUBLE,
                piece=pieces.Piece.PAWN,
                from_index=target - direction * 2,
                to_index=target
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
                            move_type=MoveType.PAWN_CAPTURE_PROMOTION,
                            piece=pieces.Piece.PAWN,
                            from_index=pawn,
                            to_index=target,
                            promotion=piece
                        )
                    )
            # Otherwise, add a normal pawn capture.
            else:
                pawn_captures.append(
                    Move(
                        move_type=MoveType.PAWN_CAPTURE,
                        piece=pieces.Piece.PAWN,
                        from_index=pawn,
                        to_index=target
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
                    move_type=MoveType.KNIGHT,
                    piece=pieces.Piece.KNIGHT,
                    from_index=knight,
                    to_index=target
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
            MoveType.BISHOP,
            pieces.Piece.BISHOP
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
            MoveType.ROOK,
            pieces.Piece.ROOK
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
            MoveType.QUEEN,
            pieces.Piece.QUEEN
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
                    move_type=MoveType.KING,
                    piece=pieces.Piece.KING,
                    from_index=king,
                    to_index=target
                )
            )
    return king_moves

# Castling move generation
def castling(occupation: int, rights: list, turn: sides.Side):
    """ Generates valid castles, taking into account castling rights.
    """
    # Return immediately if there are no valid castling moves.
    if not rights[turn]:
        return []
    
    castle_moves = []
    # Check for blockers.
    queenside_blockers = occupation & consts.CASTLING_QUEENSIDE[turn]["BLOCKERS"]
    kingside_blockers  = occupation & consts.CASTLING_KINGSIDE[turn]["BLOCKERS"]

    if MoveType.CASTLE_KINGSIDE in rights[turn] and not kingside_blockers:
        castle_moves.append(Move(MoveType.CASTLE_KINGSIDE))
    if MoveType.CASTLE_QUEENSIDE in rights[turn] and not queenside_blockers:
        castle_moves.append(Move(MoveType.CASTLE_QUEENSIDE))
    
    return castle_moves

# Duck move generation
def duck_moves(origin, occupation):
    """ Generates valid duck moves, taking into account its current
        position and board occupation.
    """
    duck_moves = []
    if origin:
        origin = utils.get_squares(origin)[0]
    else:
        origin = None
    for target in utils.get_squares(utils.invert(occupation)):
        duck_moves.append(
            Move(
                move_type=MoveType.DUCK,
                piece=pieces.Piece.DUCK,
                from_index=origin,
                to_index=target
            )
        )
    return duck_moves
