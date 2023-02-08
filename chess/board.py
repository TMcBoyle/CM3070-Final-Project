""" Chessboard representation implementation
"""
from . import consts
from . import utils
from .moves import *
from .sides import Side
from .pieces import Piece
from . import squares

from enum import Enum
from copy import deepcopy

class GameState(Enum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3

class PositionProperties:
    def __init__(self, turn: Side, castle_rights: dict, en_passant=None, move: Move=None, capture: Piece=None):
        self.turn = turn
        self.castle_rights = deepcopy(castle_rights)
        self.en_passant = en_passant
        self.move = move
        self.capture = capture

class Board:
    def __init__(self):
        self.pieces = {
            Side.WHITE: {
                Piece.PAWN: consts.INIT_WHITE_PAWNS,
                Piece.KNIGHT: consts.INIT_WHITE_KNIGHTS,
                Piece.BISHOP: consts.INIT_WHITE_BISHOPS,
                Piece.ROOK: consts.INIT_WHITE_ROOKS,
                Piece.QUEEN: consts.INIT_WHITE_QUEENS,
                Piece.KING: consts.INIT_WHITE_KING,
            },
            Side.BLACK: {
                Piece.PAWN: consts.INIT_WHITE_PAWNS,
                Piece.KNIGHT: consts.INIT_WHITE_KNIGHTS,
                Piece.BISHOP: consts.INIT_WHITE_BISHOPS,
                Piece.ROOK: consts.INIT_WHITE_ROOKS,
                Piece.QUEEN: consts.INIT_WHITE_QUEENS,
                Piece.KING: consts.INIT_WHITE_KING,
            }
        }
        
        self.white = consts.INIT_WHITE_PIECES
        self.black = consts.INIT_BLACK_PIECES
        self.duck = consts.INIT_DUCK
        self.occupied = consts.INIT_ALL_PIECES

        self.turn = Side.WHITE
        self.castle_rights = {
            Side.WHITE: [MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE],
            Side.BLACK: [MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE]
        }
        self.en_passant = None

        self.stack = []

        self.mailbox = []
        self.update_mailbox()

    def get_legal_moves(self):
        if self.turn in (Side.WHITE_DUCK, Side.BLACK_DUCK):
            return duck_moves(self.duck, self.occupied)
        
        if self.turn == Side.WHITE:
            allies = self.pieces[Side.WHITE]
            enemies = self.black
            blockers = self.white
        elif self.turn == Side.BLACK:
            allies = self.pieces[Side.BLACK]
            enemies = self.white
            blockers = self.black

        legal_moves = []
        legal_moves += pawn_pushes(allies[Piece.PAWN], self.occupied, self.turn)
        legal_moves += pawn_captures(allies[Piece.PAWN], enemies, self.turn)
        legal_moves += knight_moves(allies[Piece.KNIGHT], self.occupied, blockers)
        legal_moves += bishop_moves(allies[Piece.BISHOP], self.occupied, blockers)
        legal_moves += rook_moves(allies[Piece.ROOK], self.occupied, blockers)
        legal_moves += queen_moves(allies[Piece.QUEEN], self.occupied, blockers)
        legal_moves += king_moves(allies[Piece.KING], self.occupied, blockers)
        legal_moves += castling(
            self.occupied, self.castle_rights, self.turn
        )

        return legal_moves

    def make_move(self, move: Move):
        """ Applies the provided move to the board.
            IMPORTANT: This method assumes a legal move is passed.
        """
        # Update property stack
        self.stack.append(PositionProperties(
            self.turn,
            self.castle_rights,
            self.en_passant,
            move
        ))

        from_mask = squares.masks[move.from_index] if move.from_index is not None else None
        to_mask = squares.masks[move.to_index] if move.to_index is not None else None
        opponent = Side.WHITE if self.turn in (Side.BLACK, Side.BLACK_DUCK) else Side.BLACK

        # Duck moves
        if move.move_type == MoveType.DUCK:
            # Remove the duck if it's already on the board
            if self.duck != consts.EMPTY:
                self.occupied ^= self.duck
                self.duck ^= from_mask
            # Place the duck on the destination square
            self.duck |= to_mask
                    
        # Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            # Move the rook/king
            self.pieces[self.turn][Piece.ROOK] ^= consts.CASTLING_KINGSIDE[self.turn][Piece.ROOK]
            self.pieces[self.turn][Piece.KING] ^= consts.CASTLING_KINGSIDE[self.turn][Piece.KING]
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            # Move the rook/king
            self.pieces[self.turn][Piece.ROOK] ^= consts.CASTLING_QUEENSIDE[self.turn][Piece.ROOK]
            self.pieces[self.turn][Piece.KING] ^= consts.CASTLING_QUEENSIDE[self.turn][Piece.KING]

        # Promotions
        elif move.move_type == MoveType.PAWN_PROMOTION:
            # Remove the pawn
            self.pieces[self.turn][Piece.PAWN] ^= from_mask
            # Add the new, promoted piece
            self.pieces[self.turn][move.promotion] |= to_mask
        elif move.move_type == MoveType.PAWN_CAPTURE_PROMOTION:
            # Remove the pawn
            self.pieces[self.turn][Piece.PAWN] ^= from_mask
            # Add the new, promoted piece
            self.pieces[self.turn][move.promotion] |= to_mask
            # Find and remove the captured piece
            for piece, bitboard in self.pieces[opponent].items():
                if bitboard & to_mask:
                    bitboard ^= to_mask
                    self.stack[-1].capture = piece

        # Other moves
        else:
            # Move the piece
            self.pieces[self.turn][move.piece] ^= (from_mask | to_mask)
            # Check for captures, removing the captured piece if needed
            for piece, bitboard in self.pieces[opponent].items():
                if bitboard & to_mask:
                    bitboard ^= to_mask
                    self.stack[-1].capture = piece

    def unmake_move(self):
        """ Reverts the last played move and restores position properties
            such as castling rights.
        """
        properties = self.stack.pop()
        self.turn = properties.turn
        self.castle_rights = properties.castle_rights
        self.en_passant = properties.en_passant

        move = properties.move

        from_mask = squares.masks[move.from_index] if move.from_index is not None else None
        to_mask = squares.masks[move.to_index] if move.to_index is not None else None
        opponent = Side.WHITE if self.turn in (Side.BLACK, Side.BLACK_DUCK) else Side.BLACK

        # Duck moves
        if move.move_type == MoveType.DUCK:
            # Remove the duck if it's already on the board
            if self.duck != consts.EMPTY:
                self.occupied ^= self.duck
                self.duck ^= to_mask
            # Place the duck back on the origin square
            self.duck |= from_mask
        
        # Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            # Move the rook/king
            self.pieces[self.turn][Piece.ROOK] ^= consts.CASTLING_KINGSIDE[self.turn][Piece.ROOK]
            self.pieces[self.turn][Piece.KING] ^= consts.CASTLING_KINGSIDE[self.turn][Piece.KING]
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            # Move the rook/king
            self.pieces[self.turn][Piece.ROOK] ^= consts.CASTLING_QUEENSIDE[self.turn][Piece.ROOK]
            self.pieces[self.turn][Piece.KING] ^= consts.CASTLING_QUEENSIDE[self.turn][Piece.KING]

        # Promotions
        elif move.move_type == MoveType.PAWN_PROMOTION:
            # Add the pawn back
            self.pieces[self.turn][Piece.PAWN] |= from_mask
            # Remove the promoted piece
            self.pieces[self.turn][move.promotion] ^= to_mask
        elif move.move_type == MoveType.PAWN_CAPTURE_PROMOTION:
            # Add the pawn back
            self.pieces[self.turn][Piece.PAWN] |= from_mask
            # Remove the promoted piece
            self.pieces[self.turn][move.promotion] ^= to_mask
            # Restore the captured piece
            self.pieces[opponent][properties.capture] |= to_mask

        # Other moves
        else:
            # Move the piece back
            self.pieces[self.turn][move.piece] ^= (from_mask | to_mask)
            # Restore the captured piece
            self.pieces[opponent][properties.capture] |= to_mask

    def update_mailbox(self):
        """ Returns the current board state in mailbox format (i.e.,
            a length 64 array with characters representing the pieces)
        """
        result = [' '] * 64
        for side, group in self.pieces.items():
            for piece, bitboard in group.items():
                for square in utils.get_squares(bitboard):
                    result[square] = pieces.symbols[side][piece]
        self.mailbox = result

    def __str__(self):
        self.update_mailbox()
        result = ""
        for s in range(len(self.mailbox), 0, -8):
            result += f"{s//8}|" + ''.join(self.mailbox[s-8:s]) + '\n' 
        result += " +--------\n  ABCDEFGH"
        return result.strip('\n')
