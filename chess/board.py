""" Chessboard representation implementation
"""
from . import consts
from . import utils
from . import moves
from . import sides
from . import squares

from enum import Enum

class GameState(Enum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3

class Board:
    def __init__(self):
        self.mailbox = [
            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R', 
            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.', 
            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
            'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
        ]

        self.pieces = {
            sides.Side.WHITE: {
                "pawns":   consts.INIT_WHITE_PAWNS,
                "knights": consts.INIT_WHITE_KNIGHTS,
                "bishops": consts.INIT_WHITE_BISHOPS,
                "rooks":   consts.INIT_WHITE_ROOKS,
                "queens":  consts.INIT_WHITE_QUEENS,
                "king":    consts.INIT_WHITE_KING,
                "all":     consts.INIT_WHITE_PIECES
            },
            sides.Side.BLACK: {
                "pawns":   consts.INIT_BLACK_PAWNS,
                "knights": consts.INIT_BLACK_KNIGHTS,
                "bishops": consts.INIT_BLACK_BISHOPS,
                "rooks":   consts.INIT_BLACK_ROOKS,
                "queens":  consts.INIT_BLACK_QUEENS,
                "king":    consts.INIT_BLACK_KING,
                "all":     consts.INIT_BLACK_PIECES
            },
            "duck": {
                "duck": None
            }
        }

        self.en_passant = consts.EMPTY
        self.castle_rights = {
            sides.Side.WHITE: {
                squares.a1: True,
                squares.h1: True
            },
            sides.Side.BLACK: {
                squares.a8: True,
                squares.h8: True
            }
        }
        self.turn = sides.Side.WHITE
        self.duck_turn = False
        self.terminal = GameState.ONGOING

    def check_game_end(self):
        if self.pieces[sides.Side.WHITE]["king"] == consts.EMPTY:
            self.terminal = GameState.BLACK_WINS
        elif self.pieces[sides.Side.BLACK]["king"] == consts.EMPTY:
            self.terminal = GameState.WHITE_WINS
        return self.terminal

    def occupied(self):
        return    self.pieces[sides.Side.WHITE]["all"] \
                | self.pieces[sides.Side.BLACK]["all"] \
                | self.pieces["duck"]["duck"] if self.pieces["duck"]["duck"] else consts.EMPTY

    def empty(self):
        return utils.invert(self.occupied())

    def make_move(self, move: moves.Move):
        """ Returns a copy of this board with the provided move applied.
        """
        # Change turn if necessary and update mailbox
        if move.move_type == moves.MoveType.DUCK:
            self.turn = sides.advance_turn(self.turn)
            if '@' in self.mailbox:
                self.mailbox[self.mailbox.index('@')] = '.'
            self.mailbox[move.to_square] = '@'
        else:
            self.mailbox[move.to_square] = self.mailbox[move.from_square]
            self.mailbox[move.from_square] = '.'
        
        if move.move_type == moves.MoveType.DUCK:
            self.pieces["duck"]["duck"] = move.to_mask
        else:
            for side in self.pieces:
                if side == "duck":
                    continue
                for piece in self.pieces[side]:
                    self.pieces[side][piece] = move.apply(self.pieces[side][piece])

        self.duck_turn = not self.duck_turn

    def get_legal_moves(self):
        """ Returns a list of legal moves for the current side.
        """
        if self.duck_turn:
            return self.get_duck_moves()

        occupation = self.occupied()

        pieces = self.pieces[self.turn]
        allies = pieces["all"]
        enemies = occupation ^ allies

        pawns   = pieces["pawns"]
        knights = pieces["knights"]
        bishops = pieces["bishops"]
        rooks   = pieces["rooks"]
        queens  = pieces["queens"]
        king    = pieces["king"]
        
        legal_moves = []
        legal_moves += moves.pawn_pushes(pawns, occupation, self.turn)
        legal_moves += moves.pawn_captures(pawns, enemies, self.turn)
        legal_moves += moves.knight_moves(knights, occupation, allies)
        legal_moves += moves.bishop_moves(bishops, occupation, allies)
        legal_moves += moves.rook_moves(rooks, occupation, allies)
        legal_moves += moves.queen_moves(queens, occupation, allies)
        legal_moves += moves.king_moves(king, occupation, allies)
        
        return legal_moves

    def get_duck_moves(self):
        duck = self.pieces["duck"]["duck"]
        duck_moves = moves.duck_moves(duck, self.occupied())
        return duck_moves

    def __str__(self):
        result = ""
        for s in range(len(self.mailbox), 0, -8):
            result += f"{s//8}|" + ''.join(self.mailbox[s-8:s]) + '\n' 
        result += " +--------\n  ABCDEFGH"
        return result.strip('\n')
