""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move
from chess.utils import population_count
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

    def evaluate(self):
        white = self.board.pieces[Side.WHITE]
        black = self.board.pieces[Side.BLACK]
        
        pawn_diff   = population_count(white[Piece.PAWN])   - population_count(black[Piece.PAWN])
        knight_diff = population_count(white[Piece.KNIGHT]) - population_count(black[Piece.KNIGHT])
        bishop_diff = population_count(white[Piece.BISHOP]) - population_count(black[Piece.BISHOP])
        rook_diff   = population_count(white[Piece.ROOK])   - population_count(black[Piece.ROOK])
        queen_diff  = population_count(white[Piece.QUEEN])  - population_count(black[Piece.QUEEN])
        king_diff   = population_count(white[Piece.KING])   - population_count(black[Piece.KING])

        multiplier = 1 if self.eval_side == Side.WHITE else -1
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

    def __negamax(self, depth):
        if depth == 0:
            return self.evaluate()
        

    def search(self, depth: int=1):
        self.eval_side = self.board.turn

        best = -infinity
        best_move = None
        for move in self.board.get_legal_moves():
            self.board.make_move(move)
            score = self.evaluate()
            self.board.unmake_move()

            if score > best:
                best = score
                best_move = move

        self.board.make_move(best_move)
        duck_move = random.choice(self.board.get_legal_moves())
        self.board.unmake_move()

        return (best, best_move, duck_move)
