""" Chessboard representation implementation
"""
from bitboards import consts
from bitboards import utils
from enum import Enum

class Side(Enum):
    WHITE = 0
    BLACK = 1

class Board:
    def __init__(self):
        self.white_pawns   = consts.INIT_WHITE_PAWNS
        self.white_rooks   = consts.INIT_WHITE_ROOKS
        self.white_knights = consts.INIT_WHITE_KNIGHTS
        self.white_bishops = consts.INIT_WHITE_BISHOPS
        self.white_queens  = consts.INIT_WHITE_QUEENS
        self.white_king    = consts.INIT_WHITE_KING
        self.white_pieces  = consts.INIT_WHITE_PIECES

        self.black_pawns   = consts.INIT_BLACK_PAWNS
        self.black_rooks   = consts.INIT_BLACK_ROOKS
        self.black_knights = consts.INIT_BLACK_KNIGHTS
        self.black_bishops = consts.INIT_BLACK_BISHOPS
        self.black_queens  = consts.INIT_BLACK_QUEENS
        self.black_king    = consts.INIT_BLACK_KING
        self.black_pieces  = consts.INIT_BLACK_PIECES

        self.duck = consts.INIT_DUCK

        self.turn = Side.WHITE

    def occupied(self):
        return self.white_pieces | self.black_pieces

    def empty(self):
        return utils.invert(self.occupied())

    def get_pawn_pushes(self):
        """ Returns an array of legal pawn moves, based on whose
            turn it is (self.turn).
        """
        moves = []
        if (self.turn == Side.WHITE):
            double_pushes = utils.invert((self.white_pawns << 2) & self.occupied())
            single_pushes = utils.invert((self.white_pawns << 1) & self.occupied())
            
            

    def get_legal_moves(self):
        pass
