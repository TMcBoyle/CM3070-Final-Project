""" Chessboard representation implementation
"""

from .consts import *
from .moves import *
from .pieces import Piece, PieceType, PIECE_MASK
from .sides import Side, next_turn
from .zobrist import zbr_hash

from . import squares

from dataclasses import dataclass
from enum import IntEnum

class GameState(IntEnum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3

@dataclass
class PositionProperties:
    """ Dataclass for storing the properties of a position.
    """
    game_state: GameState
    turn: Side
    duck: int
    castle_rights: int
    en_passant: int
    capture: PieceType
    move: Move
    zbr: int

@dataclass
class PositionBoards:
    """ Dataclass for storing the bitboards of a position.
    """
    # Player pieces.
    pieces: dict[Side, PieceType] = {
        Side.WHITE: {
            PieceType.PAWN: INIT_WHITE_PAWNS,
            PieceType.KNIGHT: INIT_WHITE_KNIGHTS,
            PieceType.BISHOP: INIT_WHITE_BISHOPS,
            PieceType.ROOK: INIT_WHITE_ROOKS,
            PieceType.QUEEN: INIT_WHITE_QUEENS,
            PieceType.KING: INIT_WHITE_KING
        },
        Side.BLACK: {
            PieceType.PAWN: INIT_BLACK_PAWNS,
            PieceType.KNIGHT: INIT_BLACK_KNIGHTS,
            PieceType.BISHOP: INIT_BLACK_BISHOPS,
            PieceType.ROOK: INIT_BLACK_ROOKS,
            PieceType.QUEEN: INIT_BLACK_QUEENS,
            PieceType.KING: INIT_BLACK_KING
        }
    }
    # Aggregate bitboards, to be updated incrementally.
    duck: int = INIT_DUCK
    white: int = INIT_WHITE_PIECES
    black: int = INIT_BLACK_PIECES
    occupied: int = INIT_ALL_PIECES

class Board:
    """ Duck chess board representation.
    """
    def __init__(self):
        self.boards = PositionBoards()

        self.turn = Side.WHITE
        self.castle_rights = EMPTY
        self.en_passant = EMPTY
        self.game_state = GameState.ONGOING

        self.history = []
        self.mailbox = [
            Piece.W_ROOK, Piece.W_KNIGHT, Piece.W_BISHOP, Piece.W_QUEEN, Piece.W_KING, Piece.W_BISHOP, Piece.W_KNIGHT, Piece.W_ROOK,
            Piece.W_PAWN, Piece.W_PAWN,   Piece.W_PAWN,   Piece.W_PAWN,  Piece.W_PAWN, Piece.W_PAWN,   Piece.W_PAWN,   Piece.W_PAWN,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.B_PAWN, Piece.B_PAWN,   Piece.B_PAWN,   Piece.B_PAWN,  Piece.B_PAWN, Piece.B_PAWN,   Piece.B_PAWN,   Piece.B_PAWN,
            Piece.B_ROOK, Piece.B_KNIGHT, Piece.B_BISHOP, Piece.B_QUEEN, Piece.B_KING, Piece.B_BISHOP, Piece.B_KNIGHT, Piece.B_ROOK,
        ]

        # Initialise Zobrist Hash value.
        self.zbr = zbr_hash(self)

    def update_game_state(self):
        if self.boards.pieces[Side.WHITE][PieceType.KING] == consts.EMPTY:
            self.game_state = GameState.BLACK_WINS
        elif self.boards.pieces[Side.BLACK][PieceType.KING] == consts.EMPTY:
            self.game_state = GameState.WHITE_WINS

    def skip_move(self):
        """ Advanced the turn order without making a move.
        """
        self.turn = sides.next_turn(self.turn)

    def generate_moves(self, pseudo: bool=False):
        """ Returns a list of valid moves in the position. If
            pseudo is true, the duck is ignored and a pseudolegal move
            list is generated instead.
        """
        occupation = self.boards.occupied ^ (self.boards.duck if pseudo else EMPTY)

        # Return just the duck moves if it's a duck turn.
        if self.turn in (Side.WHITE_DUCK, Side.BLACK_DUCK):
            return duck_moves(occupation)
        
        # Set bitboards to use based on the current turn.
        pieces = self.boards.pieces[self.turn]
        allies = self.boards.white if self.turn == Side.WHITE else self.boards.black
        enemies = self.boards.white if self.turn == Side.WHITE else self.boards.black

        # Generate the moves.
        moves = []
        moves += pawn_captures(pieces[PieceType.PAWN],   enemies,    self.turn)
        moves += pawn_pushes  (pieces[PieceType.PAWN],   occupation, self.turn)
        moves += knight_moves (pieces[PieceType.KNIGHT], occupation, allies)
        moves += bishop_moves (pieces[PieceType.BISHOP], occupation, allies)
        moves += rook_moves   (pieces[PieceType.ROOK],   occupation, allies)
        moves += queen_moves  (pieces[PieceType.QUEEN],  occupation, allies)
        moves += king_moves   (pieces[PieceType.KING],   occupation, allies)
        moves += castling     (pieces[PieceType.PAWN],   occupation, allies)

        return moves

    def make_move(self, move: Move):
        """ Applies the provided move to the board.
            IMPORTANT: This method assumes a legal move is passed.
        """
        # Build position properties object and update history
        properties = PositionProperties(
            game_state=self.game_state,
            turn=self.turn,
            duck=self.boards.duck,
            castle_rights=self.castle_rights,
            en_passant=self.en_passant,
            capture=self.mailbox[move.to_index],
            move=move,
            zbr=self.zbr
        )
        # Update history
        self.history.append(properties)

        # Special cases - duck moves, castling, promotions
        if move.move_type == MoveType.DUCK:
            self.duck = squares.masks[move.to_index]
        elif move.move_type in (MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE):
            castle_masks = \
                CASTLING_KINGSIDE if move.move_type == MoveType.CASTLE_KINGSIDE \
                else CASTLING_QUEENSIDE
            # Get the relevant swap masks
            rook_swap = castle_masks[self.turn][PieceType.ROOK]
            king_swap = castle_masks[self.turn][PieceType.KING]
            # Castle
            self.boards.pieces[self.turn][PieceType.ROOK] ^= rook_swap
            self.boards.pieces[self.turn][PieceType.KING] ^= king_swap
            # Update aggregate boards
            if self.turn == Side.WHITE:
                self.boards.white ^= rook_swap | king_swap
            elif self.turn == Side.BLACK:
                self.boards.black ^= rook_swap | king_swap
            # Remove castling rights for this side
            self.castle_rights &= \
                BLACK_CASTLE_RIGHTS if self.turn == Side.WHITE else WHITE_CASTLE_RIGHTS

        # Normal moves
        else:
            # If we don't know the piece type (for manual moves), set it
            if not move.piece:
                move.piece = PieceType(self.mailbox[move.from_index] & PIECE_MASK)

            # Get move masks
            from_mask = squares.masks[move.from_index]
            to_mask = squares.masks[move.to_index]

            # Move the piece
            self.boards.pieces[self.turn][move.piece] ^= from_mask | to_mask

            # If a rook was moved, update castle rights
            if move.piece == PieceType.ROOK:
                self.castle_rights ^= from_mask

            # Check for captures, remove the captured piece if needed
            if properties.capture != Piece.EMPTY:
                target_type = PieceType(properties.capture & PIECE_MASK)
                self.boards.pieces[self.turn][target_type] ^= to_mask
                
                # If a rook was captured, update castling rights
                if target_type == PieceType.ROOK:
                    self.castle_rights ^= to_mask

            # Update aggregate boards
            if self.turn == Side.WHITE:
                self.boards.white ^= from_mask & to_mask
            elif self.turn == Side.BLACK:
                self.boards.black ^= from_mask | to_mask
        
        # Update occupied board
        self.boards.occupied = self.boards.white | self.boards.black | self.boards.duck

        # Update game state
        self.turn = sides.next_turn(self.turn)
        self.update_game_state()
