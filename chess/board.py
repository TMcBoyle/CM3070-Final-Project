""" Chessboard representation implementation
"""

from .consts import *
from .moves import *
from .pieces import Piece, PieceType, PIECE_MASK, SIDE_MASK
from .sides import Side, next_turn, opposing_side
from .zobrist import zbr_hash, zbr_update

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
    # Player pieces. Defaults to the starting position - this is
    # handled in __post_init__.
    pieces: dict[Side, PieceType] = None
    # Aggregate bitboards, to be updated incrementally.
    duck: int = INIT_DUCK
    white: int = INIT_WHITE_PIECES
    black: int = INIT_BLACK_PIECES
    occupied: int = INIT_ALL_PIECES

    def __post_init__(self):
        if not self.pieces:
            self.pieces = {
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

    def from_fen_string(string: str) -> "Board":
        """ Creates a board from a FEN-style string """
        fields = string.split(" ")
        ranks = fields[0]
        turn = fields[1]
        castle_rights = fields[2]
        en_passant = fields[3]

        board = Board()
        board.mailbox = [Piece.EMPTY] * 64
        for side in board.boards.pieces:
            for piece in board.boards.pieces[side]:
                board.boards.pieces[side][piece] = EMPTY

        idx = 0
        for rank in reversed(ranks.split("/")):
            for square in rank:
                # Empty cells
                if square.isnumeric():
                    idx += int(square)
                    continue
                # Duck
                elif square == pieces.symbols[Piece.DUCK]:
                    board.duck = squares.masks[idx]
                    board.mailbox[idx] = Piece.DUCK
                # Pieces
                else:
                    piece = pieces.symbol_lookup[square]
                    board.boards.pieces[piece & SIDE_MASK][piece & PIECE_MASK] \
                        |= squares.masks[idx]
                    board.mailbox[idx] = piece
                idx += 1
        
        # Set turn
        if turn == "w":
            board.turn = Side.WHITE
        elif turn == "w@":
            board.turn = Side.WHITE_DUCK
        elif turn == "b":
            board.turn = Side.BLACK
        elif turn == "b@":
            board.turn = Side.BLACK_DUCK

        # Set castling rights
        board.castle_rights = consts.EMPTY
        if "Q" in castle_rights:
            board.castle_rights |= squares.masks[squares.a1]
        if "K" in castle_rights:
            board.castle_rights |= squares.masks[squares.h1]
        if "q" in castle_rights:
            board.castle_rights |= squares.masks[squares.a8]
        if "k" in castle_rights:
            board.castle_rights |= squares.masks[squares.h8]

        # Set aggregate bitboards
        board.boards.white = EMPTY
        for bitboard in board.boards.pieces[Side.WHITE].values():
            board.boards.white |= bitboard
        board.boards.black = EMPTY
        for bitboard in board.boards.pieces[Side.BLACK].values():
            board.boards.black |= bitboard

        board.boards.occupied = \
            board.boards.white | board.boards.black | board.boards.duck

        return board

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
            return duck_moves(self.duck, occupation)
        
        # Set bitboards to use based on the current turn.
        pieces = self.boards.pieces[self.turn]
        allies = self.boards.white if self.turn == Side.WHITE else self.boards.black
        enemies = self.boards.white if self.turn == Side.BLACK else self.boards.black

        # Generate the moves.
        moves = []
        moves += pawn_captures(pieces[PieceType.PAWN],   enemies,    self.turn)
        moves += pawn_pushes  (pieces[PieceType.PAWN],   occupation, self.turn)
        moves += knight_moves (pieces[PieceType.KNIGHT], occupation, allies)
        moves += bishop_moves (pieces[PieceType.BISHOP], occupation, allies)
        moves += rook_moves   (pieces[PieceType.ROOK],   occupation, allies)
        moves += queen_moves  (pieces[PieceType.QUEEN],  occupation, allies)
        moves += king_moves   (pieces[PieceType.KING],   occupation, allies)
        moves += castling     (occupation, self.castle_rights, self.turn)

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

        # Special cases - duck moves and castling
        if move.move_type == MoveType.DUCK:
            self.duck = squares.masks[move.to_index]
            # Update mailbox
            if move.from_index:
                self.mailbox[move.from_index] = Piece.EMPTY
            self.mailbox[move.to_index] = Piece.DUCK
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
            # Update aggregate boards and mailbox
            if self.turn == Side.WHITE:
                self.boards.white ^= rook_swap | king_swap
                # Kingside
                if move.move_type == MoveType.CASTLE_KINGSIDE:
                    self.mailbox[squares.f1] = Piece.W_ROOK
                    self.mailbox[squares.g1] = Piece.W_KING
                    self.mailbox[squares.h1] = Piece.EMPTY
                    self.mailbox[squares.e1] = Piece.EMPTY
                # Queenside
                elif move.move_type == MoveType.CASTLE_QUEENSIDE:
                    self.mailbox[squares.d1] = Piece.W_ROOK
                    self.mailbox[squares.c1] = Piece.W_KING
                    self.mailbox[squares.a1] = Piece.EMPTY
                    self.mailbox[squares.e1] = Piece.EMPTY
            elif self.turn == Side.BLACK:
                self.boards.black ^= rook_swap | king_swap
                # Kingside
                if move.move_type == MoveType.CASTLE_KINGSIDE:
                    self.mailbox[squares.f1] = Piece.B_ROOK
                    self.mailbox[squares.g1] = Piece.B_KING
                    self.mailbox[squares.h1] = Piece.EMPTY
                    self.mailbox[squares.e1] = Piece.EMPTY
                # Queenside
                elif move.move_type == MoveType.CASTLE_QUEENSIDE:
                    self.mailbox[squares.d1] = Piece.B_ROOK
                    self.mailbox[squares.c1] = Piece.B_KING
                    self.mailbox[squares.a1] = Piece.EMPTY
                    self.mailbox[squares.e1] = Piece.EMPTY
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

            # If a rook or king was moved, update castle rights
            if move.piece == PieceType.ROOK:
                self.castle_rights ^= from_mask
            elif move.piece == PieceType.KING:
                self.castle_rights &= \
                    BLACK_CASTLE_RIGHTS if self.turn == Side.WHITE \
                    else WHITE_CASTLE_RIGHTS

            # Check for captures, remove the captured piece if needed
            if properties.capture != Piece.EMPTY:
                target_type = PieceType(properties.capture & PIECE_MASK)
                self.boards.pieces[opposing_side(self.turn)][target_type] ^= to_mask
                
                # If a rook was captured, update castling rights
                if target_type == PieceType.ROOK:
                    self.castle_rights ^= to_mask

            # Check for promotions
            if move.promotion:
                self.boards.pieces[self.turn][move.piece] ^= to_mask
                self.boards.pieces[self.turn][move.promotion] ^= to_mask

            # Update aggregate boards
            if self.turn == Side.WHITE:
                self.boards.white ^= from_mask | to_mask
            elif self.turn == Side.BLACK:
                self.boards.black ^= from_mask | to_mask

            # Update the mailbox
            final_piece = move.piece if not move.promotion else move.promotion
            self.mailbox[move.to_index] = Piece(self.turn | final_piece)
            self.mailbox[move.from_index] = Piece.EMPTY
        
        # Update occupied board and Zobrist hash
        self.boards.occupied = self.boards.white | self.boards.black | self.boards.duck
        self.zbr = zbr_update(self.zbr, self.turn, move, properties.capture)

        # Update game state
        self.turn = next_turn(self.turn)
        self.update_game_state()

    def unmake_move(self):
        """ Reverts the last played move and restores position properties such
            as castling rights.
        """
        # If no moves have been played, do nothing
        if not self.history:
            return
        
        # Get and restore position properties
        properties: PositionProperties = self.history.pop()
        self.game_state = properties.game_state
        self.turn = properties.turn
        self.duck = properties.duck
        self.castle_rights = properties.castle_rights
        self.en_passant = properties.en_passant
        self.zbr = properties.zbr

        move = properties.move

        # Special cases - duck moves, castling
        if move.move_type == MoveType.DUCK:
            # Update the mailbox - the duck position was already updated above
            self.mailbox[move.to_index] = Piece.EMPTY
            if move.from_index:
                self.mailbox[move.from_index] = Piece.DUCK
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
            
            # Update aggregate boards and mailbox
            if self.turn == Side.WHITE:
                self.boards.white ^= rook_swap | king_swap
                # Kingside
                if move.move_type == MoveType.CASTLE_KINGSIDE:
                    self.mailbox[squares.f1] = Piece.EMPTY
                    self.mailbox[squares.g1] = Piece.EMPTY
                    self.mailbox[squares.h1] = Piece.W_ROOK
                    self.mailbox[squares.e1] = Piece.W_KING
                # Queenside
                elif move.move_type == MoveType.CASTLE_QUEENSIDE:
                    self.mailbox[squares.d1] = Piece.EMPTY
                    self.mailbox[squares.c1] = Piece.EMPTY
                    self.mailbox[squares.a1] = Piece.W_ROOK
                    self.mailbox[squares.e1] = Piece.W_KING

            elif self.turn == Side.BLACK:
                self.boards.black ^= rook_swap | king_swap
                # Kingside
                if move.move_type == MoveType.CASTLE_KINGSIDE:
                    self.mailbox[squares.f8] = Piece.EMPTY
                    self.mailbox[squares.g8] = Piece.EMPTY
                    self.mailbox[squares.h8] = Piece.B_ROOK
                    self.mailbox[squares.e8] = Piece.B_KING
                # Queenside
                elif move.move_type == MoveType.CASTLE_QUEENSIDE:
                    self.mailbox[squares.d8] = Piece.EMPTY
                    self.mailbox[squares.c8] = Piece.EMPTY
                    self.mailbox[squares.a8] = Piece.B_ROOK
                    self.mailbox[squares.e8] = Piece.B_KING

        # Normal moves
        else:
            # Get move masks
            from_mask = squares.masks[move.from_index]
            to_mask = squares.masks[move.to_index]

            # Move the piece back
            self.boards.pieces[self.turn][move.piece] ^= from_mask | to_mask

            # If a piece was captured, return it
            if properties.capture != Piece.EMPTY:
                target_type = PieceType(properties.capture ^ PIECE_MASK)
                self.boards.pieces[opposing_side(self.turn)][target_type] ^= to_mask

            # Update aggregate boards
            if self.turn == Side.WHITE:
                self.boards.white ^= from_mask | to_mask
            elif self.turn == Side.BLACK:
                self.boards.black ^= from_mask | to_mask
            
            # Update the mailbox
            self.mailbox[move.to_index] = properties.capture
            self.mailbox[move.from_index] = Piece(self.turn | move.piece)
        
        # Update occupied board and Zobrist hash
        self.boards.occupied = self.boards.white | self.boards.black | self.boards.duck
        self.zbr = properties.zbr

    def __str__(self):
        result = ""
        for s in range(len(self.mailbox), 0, -8):
            result += f"{s//8}|" \
                + ''.join([pieces.symbols[p] for p in self.mailbox[s-8:s]]) \
                + '\n'
        result += " +--------\n  ABCDEFGH"
        return result
