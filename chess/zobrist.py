""" Lookup tables for Zobrist hashing.
    See https://www.chessprogramming.org/Zobrist_Hashing for 
    details on the method.
"""
from .moves import Move, MoveType
from .pieces import Piece
from .sides import Side, opposing_side
from .squares import *
from .consts import *
from .utils import get_squares

import random

_KEY_SIZE = (2 ** 64) - 1

# Fixing the random seed allows for storing e.g., opening books 
# or positions between sessions.
zobrist_rng = random.Random(271082)

_sides = [Side.WHITE, Side.WHITE_DUCK, Side.BLACK, Side.BLACK_DUCK]
_pieces = [
    Piece.PAWN, Piece.KNIGHT, Piece.BISHOP, Piece.ROOK, Piece.QUEEN, Piece.KING
]
_squares = [n for n in range(64)]

# Initialising lookup table for sides/pieces/squares
# Access as e.g., __hash_lookup[Side.WHITE][Piece.KNIGHT][squares.e4]
_piece_lookup = {
    side: {
        piece: [
            zobrist_rng.randint(0, _KEY_SIZE) for _ in _squares
        ] for piece in _pieces
    }
    for side in [Side.WHITE, Side.BLACK]
}
_duck = {
    mask: zobrist_rng.randint(0, _KEY_SIZE)
    for mask in masks
}
_duck[EMPTY] = EMPTY

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

class ZbrHash:
    def __init__(self, board):
        """ Calculates the Zobrist hash of a board from scratch.
        """
        self.pieces = [None for _ in _squares]
        self.duck = board.duck
        self.castle_rights = board.castle_rights
        self.en_passant = board.en_passant
        self.turn = board.turn

        self.hash = 0
        for side in board.pieces:
            for piece in board.pieces[side]:
                for square in get_squares(board.pieces[side][piece]):
                    self.pieces[square] = _piece_lookup[side][piece][square]
                    self.hash ^= self.pieces[square]
        self.hash ^= _duck[self.duck]
        self.hash ^= _castle_rights[board.castle_rights]
        self.hash ^= _en_passant[board.en_passant]
        self.hash ^= _turns[board.turn]
        
        self.history = [self.hash]

    def update(self, board, move: Move=None):
        """ Incrementally updates the hash. """
        if board.duck != self.duck:
            self.hash ^= self.duck
            self.hash ^= board.duck
            self.duck = board.duck
        if board.castle_rights != self.castle_rights:
            self.hash ^= self.castle_rights
            self.hash ^= board.castle_rights
            self.castle_rights = board.castle_rights
        if board.en_passant != self.en_passant:
            self.hash ^= self.en_passant
            self.hash ^= board.en_passant
            self.en_passant = board.en_passant
        if board.turn != self.turn:
            self.hash ^= _turns[self.turn]
            self.hash ^= _turns[board.turn]
            self.turn = board.turn
        
        if move and move.move_type != MoveType.DUCK:
            if self.pieces[move.from_index]:
                # Remove the moved piece
                self.hash ^= self.pieces[move.from_index]
                self.pieces[move.from_index] = None
            if self.pieces[move.to_index]:
                # Remove the target piece, if there is one
                self.hash ^= self.pieces[move.to_index]
            self.pieces[move.to_index] = _piece_lookup[
                opposing_side(board.turn)
            ][move.piece][move.to_index]

    def revert(self, properties, move: Move):
        """ Revert the hash to a previous state. """
        self.duck = properties.duck
        self.castle_rights = properties.castle_rights
        self.en_passant = properties.en_passant
        self.turn = properties.turn        
        
        if move and move.move_type is not MoveType.DUCK:
            if move.move_type == MoveType.CASTLE_QUEENSIDE:
                if properties.turn == Side.WHITE:
                    self.pieces[h1] = _piece_lookup[Side.WHITE][Piece.ROOK][h1]
                    self.pieces[e1] = _piece_lookup[Side.WHITE][Piece.KING][e1]
                elif properties.turn == Side.BLACK:
                    self.pieces[h8] = _piece_lookup[Side.BLACK][Piece.ROOK][h8]
                    self.pieces[e8] = _piece_lookup[Side.BLACK][Piece.KING][e8]
            elif move.move_type == MoveType.CASTLE_QUEENSIDE:
                if properties.turn == Side.WHITE:
                    self.pieces[a1] = _piece_lookup[Side.WHITE][Piece.ROOK][a1]
                    self.pieces[e1] = _piece_lookup[Side.WHITE][Piece.KING][e1]
                elif properties.turn == Side.BLACK:
                    self.pieces[a8] = _piece_lookup[Side.BLACK][Piece.ROOK][a8]
                    self.pieces[e8] = _piece_lookup[Side.BLACK][Piece.KING][e8]
            elif move.move_type in (MoveType.PAWN_PROMOTION, MoveType.PAWN_CAPTURE_PROMOTION):
                self.pieces[move.from_index] = \
                    _piece_lookup[properties.turn][Piece.PAWN][move.from_index]
                self.pieces[move.to_index] = \
                    _piece_lookup[properties.turn][move.promotion][move.to_index]
            else:
                self.pieces[move.from_index] = \
                    _piece_lookup[properties.turn][move.piece][move.from_index]
                if properties.capture:
                    self.pieces[move.to_index] = \
                        _piece_lookup[opposing_side(properties.turn)][properties.capture][move.to_index]
                else:
                    self.pieces[move.to_index] = None

        self.hash = properties.zbr_hash
