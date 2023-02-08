""" Chessboard representation implementation
"""
from . import consts
from . import utils
from . import moves
from . import sides
from . import pieces
from . import squares

from enum import Enum

class GameState(Enum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3

class PositionProperties:
    def __init__(self, board: "Board"):
        self.en_passant = board.en_passant
        self.turn = board.turn
        self.duck_turn = board.duck_turn
        self.castle_rights = {**board.castle_rights}

class Board:
    def __init__(self):
        self.bitboards = {
            sides.Side.WHITE: {
                pieces.Piece.PAWN:   consts.INIT_WHITE_PAWNS,
                pieces.Piece.KNIGHT: consts.INIT_WHITE_KNIGHTS,
                pieces.Piece.BISHOP: consts.INIT_WHITE_BISHOPS,
                pieces.Piece.ROOK:   consts.INIT_WHITE_ROOKS,
                pieces.Piece.QUEEN:  consts.INIT_WHITE_QUEENS,
                pieces.Piece.KING:   consts.INIT_WHITE_KING,
                "all": consts.INIT_WHITE_PIECES
            },
            sides.Side.BLACK: {
                pieces.Piece.PAWN:   consts.INIT_BLACK_PAWNS,
                pieces.Piece.KNIGHT: consts.INIT_BLACK_KNIGHTS,
                pieces.Piece.BISHOP: consts.INIT_BLACK_BISHOPS,
                pieces.Piece.ROOK:   consts.INIT_BLACK_ROOKS,
                pieces.Piece.QUEEN:  consts.INIT_BLACK_QUEENS,
                pieces.Piece.KING:   consts.INIT_BLACK_KING,
                "all": consts.INIT_BLACK_PIECES
            },
            "duck": {
                pieces.Piece.DUCK: consts.INIT_DUCK
            }
        }

        self.en_passant = consts.EMPTY
        self.turn = sides.Side.WHITE
        self.duck_turn = False
        self.castle_rights = {
            sides.Side.WHITE: consts.INIT_WHITE_ROOKS,
            sides.Side.BLACK: consts.INIT_BLACK_ROOKS
        }
        self.terminal = GameState.ONGOING

        self.stack = []

        self.update_mailbox()

    def check_game_end(self):
        if self.bitboards[sides.Side.WHITE][pieces.Piece.KING] == consts.EMPTY:
            self.terminal = GameState.BLACK_WINS
        elif self.bitboards[sides.Side.BLACK][pieces.Piece.KING] == consts.EMPTY:
            self.terminal = GameState.WHITE_WINS
        return self.terminal

    def occupied(self):
        return    self.bitboards[sides.Side.WHITE]["all"] \
                | self.bitboards[sides.Side.BLACK]["all"] \
                | (self.bitboards["duck"][pieces.Piece.DUCK] \
                    if self.bitboards["duck"][pieces.Piece.DUCK] \
                    else consts.EMPTY)

    def empty(self):
        return utils.invert(self.occupied())

    def update_bitboard(self, bitboard: int, move: moves.Move, type: pieces.Piece):
        """ Apply a move to a bitboard, returning an updated copy.
        """
        if move.from_mask is not None and move.to_mask is not None:
            # If the bitboard contains the moving piece...
            if bitboard & move.from_mask:
                # ... move it to the new position...
                bitboard = (bitboard & move.from_mask_inv) | move.to_mask
            # ... otherwise, remove the piece in the destination square and record
            # the captured piece into the move object.
            else:
                bitboard &= move.to_mask_inv
                move.capture = type
            return bitboard

    def revert_bitboard(self, bitboard: int, move: moves.Move):
        """ Revert the effect of a move on a bitboard, returning an updated copy.
        """
        pass

    def make_move(self, move: moves.Move):
        """ Returns a copy of this board with the provided move applied.
        """
        # Change turn if necessary
        if move.move_type == moves.MoveType.DUCK:
            self.turn = sides.advance_turn(self.turn)
        
        # If this is a duck move, move the duck
        if move.move_type == moves.MoveType.DUCK:
            self.bitboards["duck"][pieces.Piece.DUCK] = move.to_mask
        # If castling
        elif move.move_type == moves.MoveType.CASTLE_KINGSIDE:
            if self.turn == sides.Side.WHITE:
                self.bitboards[self.turn][pieces.Piece.KING] ^= consts.CASTLING_WHITE_KINGSIDE_KING
                self.bitboards[self.turn][pieces.Piece.ROOK] ^= consts.CASTLING_WHITE_KINGSIDE_ROOK
            elif self.turn == sides.Side.BLACK:
                self.bitboards[self.turn][pieces.Piece.KING] ^= consts.CASTLING_BLACK_KINGSIDE_KING
                self.bitboards[self.turn][pieces.Piece.ROOK] ^= consts.CASTLING_BLACK_KINGSIDE_ROOK
        elif move.move_type == moves.MoveType.CASTLE_QUEENSIDE:
            if self.turn == sides.Side.WHITE:
                self.bitboards[self.turn][pieces.Piece.KING] ^= consts.CASTLING_WHITE_QUEENSIDE_KING
                self.bitboards[self.turn][pieces.Piece.ROOK] ^= consts.CASTLING_WHITE_QUEENSIDE_ROOK
            elif self.turn == sides.Side.BLACK:
                self.bitboards[self.turn][pieces.Piece.KING] ^= consts.CASTLING_BLACK_QUEENSIDE_KING
                self.bitboards[self.turn][pieces.Piece.ROOK] ^= consts.CASTLING_BLACK_QUEENSIDE_ROOK
        # Otherwise, update the other bitboards
        else:
            for side in self.bitboards:
                if side == "duck":
                    continue
                for piece in self.bitboards[side]:
                    self.bitboards[side][piece] = self.update_bitboard(
                        self.bitboards[side][piece],
                        move,
                        piece
                    )
            # Handle promotions
            if move.move_type == moves.MoveType.PAWN_PROMOTION:
                # Remove the pawn...
                self.bitboards[self.turn][pieces.Piece.PAWN] &= move.to_mask_inv
                # ... and replace it with the promoted piece
                self.bitboards[self.turn][move.promotion] |= move.to_mask

        self.stack.append(PositionProperties(self))
        self.duck_turn = not self.duck_turn

    def unmake_move(self, move: moves.Move):
        # Restore position properties from the stack.
        pass

    def get_legal_moves(self):
        """ Returns a list of legal moves for the current side.
        """
        if self.duck_turn:
            return self.get_duck_moves()

        occupation = self.occupied()

        bitboards = self.bitboards[self.turn]
        blockers = bitboards["all"] | self.bitboards["duck"][pieces.Piece.DUCK]
        enemies = occupation ^ blockers

        pawns   = bitboards[pieces.Piece.PAWN]
        knights = bitboards[pieces.Piece.KNIGHT]
        bishops = bitboards[pieces.Piece.BISHOP]
        rooks   = bitboards[pieces.Piece.ROOK]
        queens  = bitboards[pieces.Piece.QUEEN]
        king    = bitboards[pieces.Piece.KING]
        
        legal_moves = []
        legal_moves += moves.pawn_pushes(pawns, occupation, self.turn)
        legal_moves += moves.pawn_captures(pawns, enemies, self.turn)
        legal_moves += moves.knight_moves(knights, occupation, blockers)
        legal_moves += moves.bishop_moves(bishops, occupation, blockers)
        legal_moves += moves.rook_moves(rooks, occupation, blockers)
        legal_moves += moves.queen_moves(queens, occupation, blockers)
        legal_moves += moves.king_moves(king, occupation, blockers)
        legal_moves += moves.castling(
            rooks, king, occupation, self.castle_rights[self.turn]
        )
        
        return legal_moves

    def get_duck_moves(self):
        duck = self.bitboards["duck"][pieces.Piece.DUCK]
        duck_moves = moves.duck_moves(duck, self.occupied())
        return duck_moves

    # def update_mailbox(self):
    #     """ Returns the current board state in mailbox format (i.e.,
    #         a length 64 array with characters representing the pieces)
    #     """
    #     result = [' '] * 64
    #     for side, group in self.bitboards.items():
    #         for piece, bitboard in group.items():
    #             if piece == "all":
    #                 continue
    #             for square in utils.get_squares(bitboard):
    #                 result[square] = pieces.symbols[side][piece]
    #     self.mailbox = result

    # def __str__(self):
    #     self.update_mailbox()
    #     result = ""
    #     for s in range(len(self.mailbox), 0, -8):
    #         result += f"{s//8}|" + ''.join(self.mailbox[s-8:s]) + '\n' 
    #     result += " +--------\n  ABCDEFGH"
    #     return result.strip('\n')
