""" Chessboard representation implementation
"""
from bitboards import *

class Board:
    def __init__(self):
        self.white_pawns   = INIT_WHITE_PAWNS
        self.white_rooks   = INIT_WHITE_ROOKS
        self.white_knights = INIT_WHITE_KNIGHTS
        self.white_bishops = INIT_WHITE_BISHOPS
        self.white_queens  = INIT_WHITE_QUEENS
        self.white_king    = INIT_WHITE_KING
        self.white_pieces  = INIT_WHITE_PIECES

        self.black_pawns   = INIT_BLACK_PAWNS
        self.black_rooks   = INIT_BLACK_ROOKS
        self.black_knights = INIT_BLACK_KNIGHTS
        self.black_bishops = INIT_BLACK_BISHOPS
        self.black_queens  = INIT_BLACK_QUEENS
        self.black_king    = INIT_BLACK_KING
        self.black_pieces  = INIT_BLACK_PIECES

        self.duck = INIT_DUCK

        self.turn = Side.WHITE

    def occupied(self):
        return self.white_pieces | self.black_pieces

    def empty(self):
        return invert(self.occupied())

    def get_pawn_pushes(self):
        """ Returns an array of legal pawn moves, based on whose
            turn it is (self.turn).
        """
        moves = []
        if (self.turn == Side.WHITE):
            double_pushes = invert((self.white_pawns << 2) & self.occupied())
            single_pushes = invert((self.white_pawns << 1) & self.occupied())
            
            

    def get_legal_moves(self):
        pass
