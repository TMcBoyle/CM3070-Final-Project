""" 'Swan' - a chess engine using a machine learning approach.
"""
from chess.board import Board
from chess.moves import Move, MoveType
from chess.sides import Side, opposing_side
from chess.pieces import Piece

from agent import Agent
from chess import consts
from search import Node

import random
import numpy as np
import tensorflow as tf
from math import inf as infinity

def bitboard_to_list(board: int):
    return np.array([
        [(x & 2**n) for n in range(8)] for x in board.to_bytes(8, "big")
    ])

class Swan(Agent):
    EVAL_PAWN_VALUE   = 1
    EVAL_KNIGHT_VALUE = 3
    EVAL_BISHOP_VALUE = 3.5
    EVAL_ROOK_VALUE   = 5
    EVAL_QUEEN_VALUE  = 9
    EVAL_KING_VALUE   = 100_000

    def __init__(self, model_path=None):
        self.board:     Board = Board()
        self.eval_side: Side  = None
        self.root:      Node  = Node()
        self.current:   Node  = self.root

        if model_path:
            self.model = tf.keras.models.load_model("./swan_model")
        else:    
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Input(shape=(18, 8, 8)))
            model.add(tf.keras.layers.Convolution2D(8, (3, 3), activation="relu"))
            model.add(tf.keras.layers.Convolution2D(4, (3, 3), activation="relu"))
            model.add(tf.keras.layers.GlobalAveragePooling2D())
            model.add(tf.keras.layers.Dense(32, activation="relu"))
            model.add(tf.keras.layers.Dense(16, activation="sigmoid"))
            model.add(tf.keras.layers.Dense(2, activation="softmax"))
            self.model = model

    def train(self, games: int, save_path=None):
        for _ in range(games):
            pass

        if save_path:
            tf.keras.models.save_model(save_path)

    def evaluate(self):
        data = []
        for b in self.board.pieces[Side.WHITE].values():
            data.append(bitboard_to_list(b))
        for b in self.board.pieces[Side.BLACK].values():
            data.append(bitboard_to_list(b))
        data.append(bitboard_to_list(self.board.white))
        data.append(bitboard_to_list(self.board.black))
        data.append(bitboard_to_list(self.board.duck))
        data.append(bitboard_to_list(self.board.occupied))
        data.append(bitboard_to_list(self.board.castle_rights))
        data.append(bitboard_to_list(self.board.en_passant))
        data = np.array(data)

        eval_idx = 0 if self.eval_side == Side.WHITE else 1
        return self.model(np.expand_dims(data, axis=0))[0][eval_idx]

    def get_next_move(self):
        return self.search(1)

    def play_move(self, move: Move):
        if move.move_type != MoveType.DUCK:
            if not self.current.children:
                self.current.expand(self.board.get_legal_moves())
            
            for child in self.current.children:
                if child.move == move:
                    self.current = child
        self.board.make_move(move)

    def __negamax_ab(self, node: Node, alpha: float, beta: float, depth: int):
        """ Based on pseudocode from:
            https://www.chessprogramming.org/Alpha-Beta#Negamax_Framework
        """
        if depth == 0:
            return self.evaluate()
        
        # If this node hasn't been expanded yet, do so now with
        # pseudolegal moves.
        if not node.children:
            node.expand(self.board.get_pseudolegal_moves())

        for child in sorted(node.children):
            # Set the current node and apply this move to the board
            self.board.make_move(child.move)
            # Skip the duck move
            self.board.skip_move()

            score = -self.__negamax_ab(child, -beta, -alpha, depth - 1)
            self.board.unmake_move()

            if score >= beta:
                node.score = beta
                return beta
            
            if score > alpha:
                alpha = score
        node.score = alpha
        return alpha
    
    def search(self, depth: int=1):
        self.eval_side = self.board.turn

        legal_moves = self.board.get_legal_moves()
        if not self.current.children:
            self.current.expand(legal_moves)

        best = -infinity
        best_moves = []
        # For each legal move...
        for child in sorted(self.current.children):
            # Skip illegal moves
            if child.move not in legal_moves:
                continue
            # Set the current node and apply this move to the board
            self.board.make_move(child.move)
            # Skip the duck move as this isn't considered yet to cut down search space
            self.board.skip_move()
            # Search
            score = self.__negamax_ab(child, -infinity, infinity, depth)

            # Revert the move
            self.board.unmake_move()

            if score > best - 0.05:
                best = score if score > best else best
                best_moves.append(child)

        # Pick a candidate move at random
        selected_node = random.choice(best_moves)

        self.current = selected_node
        self.board.make_move(selected_node.move)

        duck_move = random.choice(self.board.get_legal_moves())
        self.board.make_move(duck_move)

        return (best, selected_node.move, duck_move)
