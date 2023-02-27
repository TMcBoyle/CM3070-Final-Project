""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move
from chess.sides import Side, opposing_side
from chess.pieces import Piece

from agent import Agent
from chess import consts
from search import Tree, Node

import random
from math import inf as infinity

class Goose(Agent):
    EVAL_PAWN_VALUE   = 1
    EVAL_KNIGHT_VALUE = 3
    EVAL_BISHOP_VALUE = 3.5
    EVAL_ROOK_VALUE   = 5
    EVAL_QUEEN_VALUE  = 9
    EVAL_KING_VALUE   = 100_000

    def __init__(self, board: Board):
        self.board = board
        self.eval_side = board.turn
        self.tree = Tree(board)

    def evaluate(self):
        white = self.board.pieces[Side.WHITE]
        black = self.board.pieces[Side.BLACK]
        
        pawn_diff   = white[Piece.PAWN].bit_count()   - black[Piece.PAWN].bit_count()
        knight_diff = white[Piece.KNIGHT].bit_count() - black[Piece.KNIGHT].bit_count()
        bishop_diff = white[Piece.BISHOP].bit_count() - black[Piece.BISHOP].bit_count()
        rook_diff   = white[Piece.ROOK].bit_count()   - black[Piece.ROOK].bit_count()
        queen_diff  = white[Piece.QUEEN].bit_count()  - black[Piece.QUEEN].bit_count()
        king_diff   = white[Piece.KING].bit_count()   - black[Piece.KING].bit_count()

        multiplier = 1 if self.board.turn == Side.BLACK else -1
        score = 0
        score += pawn_diff   * Goose.EVAL_PAWN_VALUE   * multiplier 
        score += knight_diff * Goose.EVAL_KNIGHT_VALUE * multiplier 
        score += bishop_diff * Goose.EVAL_BISHOP_VALUE * multiplier 
        score += rook_diff   * Goose.EVAL_ROOK_VALUE   * multiplier 
        score += queen_diff  * Goose.EVAL_QUEEN_VALUE  * multiplier 
        score += king_diff   * Goose.EVAL_KING_VALUE   * multiplier

        return score

    def get_next_move(self):
        return self.search(2)

    def __negamax_ab(self, alpha: float, beta: float, depth: int):
        """ Based on pseudocode from:
            https://www.chessprogramming.org/Alpha-Beta#Negamax_Framework
        """
        if depth == 0:
            return self.evaluate()
        
        for move in self.board.get_legal_moves():
            self.board.make_move(move)
            self.board.skip_move()

            score = -self.__negamax_ab(-beta, -alpha, depth - 1)
            self.board.unmake_move()

            if score >= beta:
                return beta
            
            if score > alpha:
                alpha = score
        return alpha
        
    def search(self, depth: int=1):
        self.eval_side = self.board.turn

        best = -infinity
        best_moves = []
        for move in self.board.get_legal_moves():
            self.board.make_move(move)
            self.board.skip_move()
            score = self.__negamax_ab(-infinity, infinity, depth)
            self.board.unmake_move()

            if score > best - 0.05:
                best = score if score > best else best
                best_moves.append(move)

        selected_move = random.choice(best_moves)

        self.board.make_move(selected_move)
        duck_move = random.choice(self.board.get_legal_moves())
        self.board.unmake_move()

        return (best, selected_move, duck_move)
