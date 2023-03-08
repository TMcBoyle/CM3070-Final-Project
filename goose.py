""" 'Goose' - a chess engine using the traditional approach.
"""
from chess.board import Board
from chess.moves import Move, MoveType
from chess.sides import Side, opposing_side
from chess.pieces import PieceType

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
        self.board:     Board = Board()
        self.eval_side: Side  = self.board.turn
        self.current:   Node  = Node()
        self.stats = Stats()
        self.transpositions = {}

    def evaluate(board: Board):
        white = board.boards.pieces[Side.WHITE]
        black = board.boards.pieces[Side.BLACK]
        
        pawn_diff   = white[PieceType.PAWN].bit_count()   - black[PieceType.PAWN].bit_count()
        knight_diff = white[PieceType.KNIGHT].bit_count() - black[PieceType.KNIGHT].bit_count()
        bishop_diff = white[PieceType.BISHOP].bit_count() - black[PieceType.BISHOP].bit_count()
        rook_diff   = white[PieceType.ROOK].bit_count()   - black[PieceType.ROOK].bit_count()
        queen_diff  = white[PieceType.QUEEN].bit_count()  - black[PieceType.QUEEN].bit_count()
        king_diff   = white[PieceType.KING].bit_count()   - black[PieceType.KING].bit_count()

        multiplier = 1 if board.turn == Side.BLACK else -1
        score = 0
        score += pawn_diff   * Goose.EVAL_PAWN_VALUE   * multiplier 
        score += knight_diff * Goose.EVAL_KNIGHT_VALUE * multiplier 
        score += bishop_diff * Goose.EVAL_BISHOP_VALUE * multiplier 
        score += rook_diff   * Goose.EVAL_ROOK_VALUE   * multiplier 
        score += queen_diff  * Goose.EVAL_QUEEN_VALUE  * multiplier 
        score += king_diff   * Goose.EVAL_KING_VALUE   * multiplier

        return score

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
        self.board.make_move(move)

    def __negamax_ab(self, node: Node, alpha: float, beta: float, depth: int):
        """ Based on pseudocode from:
            https://www.chessprogramming.org/Alpha-Beta#Negamax_Framework
        """
        if depth == 0:
            node.score = Goose.evaluate(self.board)
            node.zbr = self.board.zbr
            return node.score
        
        # If this node hasn't been expanded yet, do so now with
        # pseudolegal moves.
        if not node.children:
            node.expand(self.board.generate_moves(pseudo=True))
        node.children.sort()

        for idx, child in enumerate(node.children):
            self.stats.nodes_searched += 1
            # Set the current node and apply this move to the board
            self.board.make_move(child.move)
            # Skip the duck move
            self.board.skip_move()

            child.zbr = self.board.zbr
            if child.zbr in self.transpositions:
                self.stats.transpositions += 1
                node.children[idx] = self.transpositions[child.zbr]
            else:
                self.transpositions[child.zbr] = child
                child.score = -self.__negamax_ab(child, -beta, -alpha, depth - 1)

            self.board.unmake_move()

            if child.score >= beta:
                self.stats.alpha_beta_cutoffs += 1
                node.score = beta
                return beta
            
            if child.score > alpha:
                alpha = child.score
        node.score = alpha
        return alpha
        
    def search(self, depth: int=1):
        self.eval_side = self.board.turn

        legal_moves = self.board.generate_moves()
        if not self.current.children:
            self.current.expand(legal_moves)
        self.current.children.sort()

        best = -infinity
        best_moves = []
        # For each legal move...
        for idx, child in enumerate(self.current.children):
            # Skip illegal moves
            if child.move not in legal_moves:
                continue
            # Set the current node and apply this move to the board
            self.board.make_move(child.move)
            # Skip the duck move as this isn't considered yet to cut down search space
            self.board.skip_move()
            # Search
            self.stats.nodes_searched += 1
            child.zbr = self.board.zbr
            if child.zbr in self.transpositions:
                self.stats.transpositions += 1
                self.current.children[idx] = self.transpositions[child.zbr]
            else:
                self.transpositions[child.zbr] = child
                child.score = self.__negamax_ab(child, -infinity, infinity, depth)

            # Revert the move
            self.board.unmake_move()

            if child.score > best - 0.05:
                best = child.score if child.score > best else best
                best_moves.append(child)

        # Pick a candidate move at random
        selected_node = random.choice(best_moves)

        self.current = selected_node
        self.board.make_move(selected_node.move)

        duck_move = random.choice(self.board.generate_moves())
        self.board.make_move(duck_move)

        return (best, selected_node.move, duck_move)
