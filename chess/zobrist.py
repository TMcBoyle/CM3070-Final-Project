""" Lookup tables for Zobrist hashing.
    See https://www.chessprogramming.org/Zobrist_Hashing for 
    details on the method.
"""
from .moves import Move, MoveType
from .pieces import Piece, PieceType
from .sides import Side, opposing_side
from .squares import *
from .consts import *
from .utils import get_squares

import random

_KEY_SIZE = (2 ** 64) - 1

# Fixing the random seed allows for storing e.g., opening books 
# or positions between sessions.
zobrist_rng = random.Random(271082) # 271082

_sides = [Side.WHITE, Side.WHITE_DUCK, Side.BLACK, Side.BLACK_DUCK]
_pieces = [
    p for p in Piece
]
_squares = [n for n in range(64)]

# Initialising lookup tables
_piece_lookup = {
    piece: [zobrist_rng.randint(0, _KEY_SIZE) for _ in _squares]
    for piece in _pieces
}

# Initialising other terms
_turns = {
    side: zobrist_rng.randint(0, _KEY_SIZE)
    for side in _sides
}

# All possible castling rights configurations
_castle_rights = {
    EMPTY: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[h1]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[h1]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[a8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[h1] | masks[a8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[h1] | masks[a8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[h1] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[h1] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a8] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[a1] | masks[a8] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    masks[h1] | masks[a8] | masks[h8]: zobrist_rng.randint(0, _KEY_SIZE),
    INIT_CASTLE_RIGHTS: zobrist_rng.randint(0, _KEY_SIZE),
}

# En Passant
_en_passant = {
    file: zobrist_rng.randint(0, _KEY_SIZE) for file in LOOKUP_FILE
}
_en_passant[EMPTY] = EMPTY

def zbr_hash(board):
    """ Calculates the Zobrist hash of a board from scratch.
    """
    zbr = 0
    for idx, piece in enumerate(board.mailbox):
        zbr ^= _piece_lookup[piece][idx]
    zbr ^= _castle_rights[board.castle_rights]
    zbr ^= _en_passant[board.en_passant]
    zbr ^= _turns[board.turn]
    
    return zbr

def zbr_update(zbr: int, side: Side, move: Move, capture: Piece=None):
    """ Updates a Zobrist hash based on a given move.
    """
    # Castling
    if move.move_type in (MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE):
        # Set variables depending on the type/side of the castling
        castling_lookup = \
            CASTLING_KINGSIDE if move.move_type == MoveType.CASTLE_KINGSIDE \
            else CASTLING_QUEENSIDE
        king_piece = Piece.W_KING if side == Side.WHITE else Piece.B_KING
        rook_piece = Piece.W_ROOK if side == Side.WHITE else Piece.B_ROOK

        # Update the hash
        zbr ^= _piece_lookup[king_piece][castling_lookup["KING_SQUARES"][0]]
        zbr ^= _piece_lookup[king_piece][castling_lookup["KING_SQUARES"][1]]
        zbr ^= _piece_lookup[rook_piece][castling_lookup["ROOK_SQUARES"][0]]
        zbr ^= _piece_lookup[rook_piece][castling_lookup["ROOK_SQUARES"][1]]
    # Update the moved piece
    else:
        if move.from_index:
            zbr ^= _piece_lookup[move.piece][move.from_index]
        zbr ^= _piece_lookup[move.piece][move.to_index]
        # Remove the captured piece, if applicable
        if capture != Piece.EMPTY:
            zbr ^= _piece_lookup[capture][move.to_index]
