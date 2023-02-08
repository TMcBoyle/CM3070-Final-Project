from chess.board import Board
from chess.pieces import Piece
from chess import utils
from chess import sides

import random

class Node:
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.children = []

    def add_children(self, children: list):
        for child in children:
            self.children.append(Node(child, self))

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
        return self.search(board)

    def search(self, board: Board, depth=1):
        root = Node()
        root.add_children(board.get_legal_moves()) # Get candidate moves

        best = None
        next_move = None
        for candidate in root.children:
            board.make_move(candidate.move)
            score = self.evaluate(board)
            board.unmake_move()

            if best is None or score - best > 0.2:
                best = score
                next_move = candidate.move

        return next_move

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
