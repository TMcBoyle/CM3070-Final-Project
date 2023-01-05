""" Chessboard representation implementation
"""
import copy

from . import consts
from . import utils
from . import moves
from . import sides
from . import squares

from enum import Enum

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
            sides.Side.DUCK: {
                "duck": consts.INIT_DUCK
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

    def occupied(self):
        return    self.pieces[sides.Side.WHITE]["all"] \
                | self.pieces[sides.Side.BLACK]["all"] \
                | self.pieces[sides.Side.DUCK]["duck"]

    def empty(self):
        return utils.invert(self.occupied())

    def make_move(self, move: moves.Move):
        """ Returns a copy of this board with the provided move applied.
        """
        # Change turn
        self.turn = sides.alternate(self.turn)

        # Update mailbox
        self.mailbox[move.to_square] = self.mailbox[move.from_square]
        self.mailbox[move.from_square] = '.'

        for side in self.pieces:
            for piece in self.pieces[side]:
                self.pieces[side][piece] = move.apply(self.pieces[side][piece])

    def get_legal_moves(self):
        """ Returns a list of legal moves for the current side.
        """
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

    def __str__(self):
        result = f'{"White" if self.turn == sides.Side.WHITE else "Black"} to move.\n'
        for s in range(len(self.mailbox), 0, -8):
            result += ''.join(self.mailbox[s-8:s]) + '\n'
        return result.strip('\n')
