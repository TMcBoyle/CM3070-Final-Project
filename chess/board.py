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
    def __init__(self, turn: Side, castle_rights: dict, duck=None, en_passant=None, game_state: GameState=None, move: Move=None, capture: Piece=None):
        self.turn = turn
        self.castle_rights = deepcopy(castle_rights)
        self.duck = duck
        self.en_passant = en_passant
        self.game_state = game_state
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
                Piece.PAWN: consts.INIT_BLACK_PAWNS,
                Piece.KNIGHT: consts.INIT_BLACK_KNIGHTS,
                Piece.BISHOP: consts.INIT_BLACK_BISHOPS,
                Piece.ROOK: consts.INIT_BLACK_ROOKS,
                Piece.QUEEN: consts.INIT_BLACK_QUEENS,
                Piece.KING: consts.INIT_BLACK_KING,
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
        self.game_state = GameState.ONGOING

        self.stack = []

        self.mailbox = []
        self.update_mailbox()

    def update_game_state(self):
        if self.pieces[Side.WHITE][Piece.KING] == consts.EMPTY:
            self.game_state = GameState.BLACK_WINS
        elif self.pieces[Side.BLACK][Piece.KING] == consts.EMPTY:
            self.game_state = GameState.WHITE_WINS

    def get_legal_moves(self):
        if self.turn in (Side.WHITE_DUCK, Side.BLACK_DUCK):
            return duck_moves(self.occupied)
        
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
            self.duck,
            self.en_passant,
            self.game_state,
            move
        ))

        from_mask = squares.masks[move.from_index] if move.from_index is not None else None
        to_mask = squares.masks[move.to_index] if move.to_index is not None else None
        opponent = Side.WHITE if self.turn in (Side.BLACK, Side.BLACK_DUCK) else Side.BLACK

        # Duck moves
        if move.move_type == MoveType.DUCK:
            self.duck = to_mask
        
        # Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            # Move the rook/king
            rook_swap = consts.CASTLING_KINGSIDE[self.turn][Piece.ROOK]
            king_swap = consts.CASTLING_KINGSIDE[self.turn][Piece.KING]
            self.pieces[self.turn][Piece.ROOK] ^= rook_swap
            self.pieces[self.turn][Piece.KING] ^= king_swap
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            # Move the rook/king
            rook_swap = consts.CASTLING_QUEENSIDE[self.turn][Piece.ROOK]
            king_swap = consts.CASTLING_QUEENSIDE[self.turn][Piece.KING]
            self.pieces[self.turn][Piece.ROOK] ^= rook_swap
            self.pieces[self.turn][Piece.KING] ^= king_swap

        # Promotions
        elif move.move_type == MoveType.PAWN_PROMOTION:
            # Remove the pawn
            self.pieces[self.turn][Piece.PAWN] ^= from_mask
            # Add the new, promoted piece
            self.pieces[self.turn][move.promotion] |= to_mask
            # Update aggregated bitboards
        elif move.move_type == MoveType.PAWN_CAPTURE_PROMOTION:
            # Remove the pawn
            self.pieces[self.turn][Piece.PAWN] ^= from_mask
            # Add the new, promoted piece
            self.pieces[self.turn][move.promotion] |= to_mask
            # Find and remove the captured piece
            for piece in self.pieces[opponent]:
                if self.pieces[opponent][piece] & to_mask:
                    self.pieces[opponent][piece] ^= to_mask
                    self.stack[-1].capture = piece
                    break

        # Other moves
        else:
            # Move the piece
            if move.piece:
                self.pieces[self.turn][move.piece] ^= (from_mask | to_mask)
            else:
                # For manual moves, we don't know which piece is being move so we have
                # to search for it.
                for piece in self.pieces[self.turn]:
                    if self.pieces[self.turn][piece] & from_mask:
                        self.pieces[self.turn][piece] ^= (from_mask | to_mask)
                        move.piece = piece
                        break
            # Check for captures, removing the captured piece if needed
            for piece in self.pieces[opponent]:
                if self.pieces[opponent][piece] & to_mask:
                    self.pieces[opponent][piece] ^= to_mask
                    self.stack[-1].capture = piece
                    break

        # Update aggregate bitboards
        self.white = consts.EMPTY
        for bitboard in self.pieces[Side.WHITE].values():
            self.white |= bitboard
        self.black = consts.EMPTY
        for bitboard in self.pieces[Side.BLACK].values():
            self.black |= bitboard
        self.occupied = self.duck | self.white | self.black

        self.turn = sides.advance_turn(self.turn)
        self.update_game_state()

    def unmake_move(self):
        """ Reverts the last played move and restores position properties
            such as castling rights.
        """
        if not self.stack:
            return
        properties = self.stack.pop()
        self.turn = properties.turn
        self.castle_rights = properties.castle_rights
        self.en_passant = properties.en_passant
        self.game_state = properties.game_state

        move = properties.move

        from_mask = squares.masks[move.from_index] if move.from_index is not None else None
        to_mask = squares.masks[move.to_index] if move.to_index is not None else None
        opponent = Side.WHITE if self.turn in (Side.BLACK, Side.BLACK_DUCK) else Side.BLACK
        
        # Duck
        if move.move_type == MoveType.DUCK:
            self.duck = properties.duck

        # Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            # Move the rook/king
            rook_swap = consts.CASTLING_KINGSIDE[self.turn][Piece.ROOK]
            king_swap = consts.CASTLING_KINGSIDE[self.turn][Piece.KING]
            self.pieces[self.turn][Piece.ROOK] ^= rook_swap
            self.pieces[self.turn][Piece.KING] ^= king_swap
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            # Move the rook/king
            rook_swap = consts.CASTLING_QUEENSIDE[self.turn][Piece.ROOK]
            king_swap = consts.CASTLING_QUEENSIDE[self.turn][Piece.KING]
            self.pieces[self.turn][Piece.ROOK] ^= rook_swap
            self.pieces[self.turn][Piece.KING] ^= king_swap

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
            if properties.capture:
                self.pieces[opponent][properties.capture] |= to_mask

    def update_mailbox(self):
        """ Returns the current board state in mailbox format (i.e.,
            a length 64 array with characters representing the pieces)
        """
        result = [' '] * 64
        for side in self.pieces:
            for piece, bitboard in self.pieces[side].items():
                for square in utils.get_squares(bitboard):
                    result[square] = pieces.symbols[side][piece]
        if self.duck != consts.EMPTY:
            result[utils.get_squares(self.duck)[0]] = pieces.symbols[Piece.DUCK]

        self.mailbox = result

    def __str__(self):
        self.update_mailbox()
        result = ""
        for s in range(len(self.mailbox), 0, -8):
            result += f"{s//8}|" + ''.join(self.mailbox[s-8:s]) + '\n' 
        result += " +--------\n  ABCDEFGH"
        return result.strip('\n')
