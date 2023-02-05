from chess.board import Board
from chess.pieces import Piece
from chess import utils
from chess import sides
from tree import Tree

import random

class Goose:
    PAWN_VALUE = 1
    KNIGHT_VALUE = 3
    BISHOP_VALUE = 3.5
    ROOK_VALUE = 5
    QUEEN_VALUE = 9
    KING_VALUE = 100_000

    def __init__(self):
        pass
    
    def get_next_move(self, board: Board):
        self.search_tree = Tree(root=board)
        return self.search()

    def search(self):
        self.search_tree.grow()

        best = None
        best_move = None
        for move, child in self.search_tree.root.children.items():
            score = self.evaluate(child.state)
            if best is None or score > best:
                best = score
                best_move = move
        return best_move

    def evaluate(self, board: Board):
        side = board.turn
        opponent = sides.advance_turn(side)
        
        score = 0
        # Ally pieces
        score += utils.population_count(board.bitboards[side][Piece.PAWN])   * Goose.PAWN_VALUE
        score += utils.population_count(board.bitboards[side][Piece.KNIGHT]) * Goose.KNIGHT_VALUE
        score += utils.population_count(board.bitboards[side][Piece.BISHOP]) * Goose.BISHOP_VALUE
        score += utils.population_count(board.bitboards[side][Piece.ROOK])   * Goose.ROOK_VALUE
        score += utils.population_count(board.bitboards[side][Piece.QUEEN])  * Goose.QUEEN_VALUE
        score += utils.population_count(board.bitboards[side][Piece.KING])   * Goose.KING_VALUE
        # Enemy pieces
        score -= utils.population_count(board.bitboards[opponent][Piece.PAWN])   * Goose.PAWN_VALUE
        score -= utils.population_count(board.bitboards[opponent][Piece.KNIGHT]) * Goose.KNIGHT_VALUE
        score -= utils.population_count(board.bitboards[opponent][Piece.BISHOP]) * Goose.BISHOP_VALUE
        score -= utils.population_count(board.bitboards[opponent][Piece.ROOK])   * Goose.ROOK_VALUE
        score -= utils.population_count(board.bitboards[opponent][Piece.QUEEN])  * Goose.QUEEN_VALUE
        score -= utils.population_count(board.bitboards[opponent][Piece.KING])   * Goose.KING_VALUE

        return score
