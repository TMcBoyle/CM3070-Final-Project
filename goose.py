""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move, MoveType
from chess.sides import Side, opposing_side
from chess.pieces import PieceType
from chess.search.algorithms import alpha_beta

from agent import Agent
from chess import consts
from chess.search.node import Node

import random
from dataclasses import dataclass
from math import inf as infinity

@dataclass
class Stats:
    nodes_searched: int = 0
    transpositions: int = 0
    alpha_beta_cutoffs: int = 0

class Goose(Agent):
    EVAL_PAWN_VALUE   = 1
    EVAL_KNIGHT_VALUE = 3
    EVAL_BISHOP_VALUE = 3.5
    EVAL_ROOK_VALUE   = 5
    EVAL_QUEEN_VALUE  = 9
    EVAL_KING_VALUE   = 100_000

    def __init__(self):
        self.board: Board = Board()
        self.current: Node  = Node()
        self.stats = Stats()
        self.transpositions = {}

    def evaluate(board: Board, **kwargs: dict):
        white = board.boards.pieces[Side.WHITE]
        black = board.boards.pieces[Side.BLACK]
        
        pawn_diff   = white[PieceType.PAWN].bit_count()   - black[PieceType.PAWN].bit_count()
        knight_diff = white[PieceType.KNIGHT].bit_count() - black[PieceType.KNIGHT].bit_count()
        bishop_diff = white[PieceType.BISHOP].bit_count() - black[PieceType.BISHOP].bit_count()
        rook_diff   = white[PieceType.ROOK].bit_count()   - black[PieceType.ROOK].bit_count()
        queen_diff  = white[PieceType.QUEEN].bit_count()  - black[PieceType.QUEEN].bit_count()
        king_diff   = white[PieceType.KING].bit_count()   - black[PieceType.KING].bit_count()

        score = 0
        score += pawn_diff   * Goose.EVAL_PAWN_VALUE 
        score += knight_diff * Goose.EVAL_KNIGHT_VALUE 
        score += bishop_diff * Goose.EVAL_BISHOP_VALUE 
        score += rook_diff   * Goose.EVAL_ROOK_VALUE 
        score += queen_diff  * Goose.EVAL_QUEEN_VALUE 
        score += king_diff   * Goose.EVAL_KING_VALUE

        return score

    def get_next_move(self):
        return self.search()

    def play_move(self, move: Move):
        if move.move_type != MoveType.DUCK:
            if not self.current.children:
                self.current.expand(self.board.generate_moves())
            
            for child in self.current.children:
                if child.move == move:
                    self.current = child
                    self.current.parent = None
                    break
        self.board.make_move(move)
        
    def search(self, depth: int=2):
        self.eval_side = self.board.turn
        result = alpha_beta(self.board, self.current, depth, Goose.evaluate)

        return (self.current.score, result[0], result[1])
