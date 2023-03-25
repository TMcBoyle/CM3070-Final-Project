""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move, MoveType, KING_TEMPLATES
from chess.sides import Side, opposing_side
from chess.pieces import PieceType
from chess.search.algorithms import alpha_beta

from agent import Agent
from chess import consts
from chess.utils import ls1b_index
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
    EVAL_FREEDOM_VALUE = 0.01
    EVAL_KING_SAFETY_VALUE = 1

    def __init__(self):
        self.board: Board = Board()
        self.current: Node  = Node()
        self.stats = Stats()
        self.transpositions = {}

    def eval_material(board: Board):
        white = board.boards.pieces[Side.WHITE]
        black = board.boards.pieces[Side.BLACK]

        pawn_diff   = white[PieceType.PAWN].bit_count()   - black[PieceType.PAWN].bit_count()
        knight_diff = white[PieceType.KNIGHT].bit_count() - black[PieceType.KNIGHT].bit_count()
        bishop_diff = white[PieceType.BISHOP].bit_count() - black[PieceType.BISHOP].bit_count()
        rook_diff   = white[PieceType.ROOK].bit_count()   - black[PieceType.ROOK].bit_count()
        queen_diff  = white[PieceType.QUEEN].bit_count()  - black[PieceType.QUEEN].bit_count()
        king_diff   = white[PieceType.KING].bit_count()   - black[PieceType.KING].bit_count()

        material_score = 0
        material_score += pawn_diff   * Goose.EVAL_PAWN_VALUE 
        material_score += knight_diff * Goose.EVAL_KNIGHT_VALUE 
        material_score += bishop_diff * Goose.EVAL_BISHOP_VALUE 
        material_score += rook_diff   * Goose.EVAL_ROOK_VALUE 
        material_score += queen_diff  * Goose.EVAL_QUEEN_VALUE 
        material_score += king_diff   * Goose.EVAL_KING_VALUE

        return material_score

    def eval_freedom(board: Board):
        freedom_score = 0

        original_side = board.turn
        # White freedom
        board.skip_move(Side.WHITE)
        freedom_score += len(board.generate_moves(True)) * Goose.EVAL_FREEDOM_VALUE
        # Black freedom
        board.skip_move(Side.BLACK)
        freedom_score -= len(board.generate_moves(True)) * Goose.EVAL_FREEDOM_VALUE
        # Return board turn to original state
        board.skip_move(original_side)

        return freedom_score

    def eval_king_safety(board: Board):
        king_safety_score = 0

        # White king safety
        white_king = board.boards.pieces[Side.WHITE][PieceType.KING]
        white_occupancy = board.boards.white
        if white_king != consts.EMPTY:
            white_king_safety = \
                (KING_TEMPLATES[ls1b_index(white_king)] & white_occupancy).bit_count() * Goose.EVAL_KING_SAFETY_VALUE
        else:
            white_king_safety = 0

        # Black king safety
        black_king = board.boards.pieces[Side.BLACK][PieceType.KING]
        black_occupancy = board.boards.black
        if black_king != consts.EMPTY:
            black_king_safety = \
                (KING_TEMPLATES[ls1b_index(black_king)] & black_occupancy).bit_count()  * Goose.EVAL_KING_SAFETY_VALUE
        else:
            black_king_safety = 0
        
        king_safety_score += white_king_safety - black_king_safety

        return king_safety_score

    def evaluate(board: Board, **kwargs: dict):
        score = 0
        
        score += Goose.eval_material(board)
        score += Goose.eval_freedom(board)
        score += Goose.eval_king_safety(board)

        return score

    def reset(self):
        self.board: Board = Board()
        self.current: Node  = Node()
        self.stats = Stats()
        self.transpositions = {}

    def get_next_move(self):
        return self.search(3)

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

    def __str__(self):
        return f"<Goose v3>"
