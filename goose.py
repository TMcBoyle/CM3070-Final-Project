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
    def __init__(self, board: Board):
        self.board = board

    def evaluate(self):
        agent = self.board.turn
        opponent = Side.BLACK if agent in (Side.WHITE, Side.WHITE_DUCK) else Side.WHITE

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
        return self.search(1)[1:]

    def __negamax(self, node: Node, depth: int):
        if depth == 0:
            return self.evaluate()
        
        maximum = None
        for move in node.children:
            self.board.make_move(move.move)
            for duck in move.children:
                self.board.make_move(duck.move)
                score = -self.__negamax(duck, depth - 1)
                self.board.unmake_move()

                if maximum is None or score > maximum[0]:
                    maximum = (score, move.move, duck.move)
            self.board.unmake_move()

        return maximum

    def search(self, depth: int=1):
        tree = Tree(self.board)
        tree.grow(tree.root, depth * 2)

        return self.__negamax(tree.root, depth)
