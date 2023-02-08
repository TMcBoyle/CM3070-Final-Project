""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move
from chess.utils import population_count
from chess.sides import Side
from chess.pieces import Piece
from search import Tree, Node
from agent import Agent

EVAL_PAWN_VALUE   = 1
EVAL_KNIGHT_VALUE = 3
EVAL_BISHOP_VALUE = 3.5
EVAL_ROOK_VALUE   = 5
EVAL_QUEEN_VALUE  = 9
EVAL_KING_VALUE   = 100_000

class Goose(Agent):
    def evaluate(self, board: Board):
        score = 0
        
        score += population_count(board.pieces[Side.WHITE][Piece.PAWN])   * EVAL_PAWN_VALUE
        score += population_count(board.pieces[Side.WHITE][Piece.KNIGHT]) * EVAL_KNIGHT_VALUE
        score += population_count(board.pieces[Side.WHITE][Piece.BISHOP]) * EVAL_BISHOP_VALUE
        score += population_count(board.pieces[Side.WHITE][Piece.ROOK])   * EVAL_ROOK_VALUE
        score += population_count(board.pieces[Side.WHITE][Piece.QUEEN])  * EVAL_QUEEN_VALUE
        score += population_count(board.pieces[Side.WHITE][Piece.KING])   * EVAL_KING_VALUE

        score -= population_count(board.pieces[Side.BLACK][Piece.PAWN])   * EVAL_PAWN_VALUE
        score -= population_count(board.pieces[Side.BLACK][Piece.KNIGHT]) * EVAL_KNIGHT_VALUE
        score -= population_count(board.pieces[Side.BLACK][Piece.BISHOP]) * EVAL_BISHOP_VALUE
        score -= population_count(board.pieces[Side.BLACK][Piece.ROOK])   * EVAL_ROOK_VALUE
        score -= population_count(board.pieces[Side.BLACK][Piece.QUEEN])  * EVAL_QUEEN_VALUE
        score -= population_count(board.pieces[Side.BLACK][Piece.KING])   * EVAL_KING_VALUE

        return score

    

    def get_next_move(self, board: Board):
        turn = board.turn
        sign = 1 if turn in (Side.WHITE, Side.WHITE_DUCK) else -1
        moves = board.get_legal_moves()

        best = None
        best_move = None
        for move in moves:
            board.make_move(move)
            current = sign * self.evaluate(board)
            if best is None or current > best:
                best = current
                best_move = move
            board.unmake_move()
        return best_move
