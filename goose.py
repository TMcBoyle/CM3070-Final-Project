""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move
from chess.utils import population_count
from chess.sides import Side
from chess.pieces import Piece

from agent import Agent
from chess import consts
from search import Tree, Node

import random
from math import inf as infinity

EVAL_PAWN_VALUE   = 1
EVAL_KNIGHT_VALUE = 3
EVAL_BISHOP_VALUE = 3.5
EVAL_ROOK_VALUE   = 5
EVAL_QUEEN_VALUE  = 9
EVAL_KING_VALUE   = 100_000

class Goose(Agent):
    def __init__(self, board: Board):
        self.board = board

    def evaluate(self):
        agent =    Side.WHITE if self.board.turn in (Side.WHITE, Side.WHITE_DUCK) else Side.BLACK
        opponent = Side.BLACK if agent     in (Side.WHITE, Side.WHITE_DUCK) else Side.WHITE
        
        score = 0
        
        score += population_count(self.board.pieces[agent][Piece.PAWN])   * EVAL_PAWN_VALUE
        score += population_count(self.board.pieces[agent][Piece.KNIGHT]) * EVAL_KNIGHT_VALUE
        score += population_count(self.board.pieces[agent][Piece.BISHOP]) * EVAL_BISHOP_VALUE
        score += population_count(self.board.pieces[agent][Piece.ROOK])   * EVAL_ROOK_VALUE
        score += population_count(self.board.pieces[agent][Piece.QUEEN])  * EVAL_QUEEN_VALUE
        score += population_count(self.board.pieces[agent][Piece.KING])   * EVAL_KING_VALUE

        score -= population_count(self.board.pieces[opponent][Piece.PAWN])   * EVAL_PAWN_VALUE
        score -= population_count(self.board.pieces[opponent][Piece.KNIGHT]) * EVAL_KNIGHT_VALUE
        score -= population_count(self.board.pieces[opponent][Piece.BISHOP]) * EVAL_BISHOP_VALUE
        score -= population_count(self.board.pieces[opponent][Piece.ROOK])   * EVAL_ROOK_VALUE
        score -= population_count(self.board.pieces[opponent][Piece.QUEEN])  * EVAL_QUEEN_VALUE
        score -= population_count(self.board.pieces[opponent][Piece.KING])   * EVAL_KING_VALUE

        return score

    def get_next_move(self):
        return self.search(3)

    def __negamax(self, node: Node, depth: int):
        if depth <= 0:
            return self.evaluate()
        
        node.expand()

        maximum = -infinity
        for move in node.children:
            self.board.make_move(move.move)
            self.board.skip_move()
            score = -self.__negamax(move, depth - 1)
            self.board.unmake_move()

            if score > maximum:
                maximum = score

        return maximum

    def search(self, depth: int=1):
        tree = Tree(self.board)
        tree.root.expand()

        best = (-infinity, None, None)
        for node in tree.root.children:
            self.board.make_move(node.move)
            self.board.skip_move() # Skip the duck move to cut down search space

            score = self.__negamax(node, depth - 1)
            self.board.unmake_move()

            if score > best[0]:
                best = (score, node.move)

        self.board.make_move(best[1])
        # Get the duck move
        best = (score, node.move, random.choice(self.board.get_legal_moves()))
        self.board.unmake_move()

        return best
