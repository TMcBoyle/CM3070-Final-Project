""" 'Swan' - a chess engine using a machine learning approach.
"""
from chess.board import Board
from chess.moves import Move
from chess.sides import Side, opposing_side
from chess.pieces import Piece

from agent import Agent
from chess import consts
from search import Tree, Node

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

    def __init__(self, board: Board, model_path=None):
        self.board = board
        self.eval_side = board.turn
        self.tree = Tree(board)
        if model_path:
            self.model = tf.keras.models.load_model("./swan_model")
        else:    
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Input(shape=(18, 8, 8)))
            model.add(tf.keras.layers.Convolution2D(8, (3, 3), activation="relu"))
            model.add(tf.keras.layers.Convolution2D(32, (3, 3), activation="relu"))
            model.add(tf.keras.layers.GlobalAveragePooling2D())
            model.add(tf.keras.layers.Dense(64, activation="relu"))
            model.add(tf.keras.layers.Dense(16, activation="sigmoid"))
            model.add(tf.keras.layers.Dense( 2, activation="softmax"))
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

        return self.model(np.expand_dims(data, axis=0))[0][0]

    def get_next_move(self):
        return self.search(1)

    def __negamax_ab(self, alpha: float, beta: float, depth: int):
        """ Based on pseudocode from:
            https://www.chessprogramming.org/Alpha-Beta#Negamax_Framework
        """
        if depth == 0:
            return self.evaluate()
        
        for move in self.board.get_legal_moves():
            self.board.make_move(move)
            self.board.skip_move()

            score = -self.__negamax_ab(-beta, -alpha, depth - 1)
            self.board.unmake_move()

            if score >= beta:
                return beta
            
            if score > alpha:
                alpha = score
        return alpha
    
    def search(self, depth: int=1):
        self.eval_side = self.board.turn

        best = -infinity
        best_move = []
        for move in self.board.get_legal_moves():
            self.board.make_move(move)
            self.board.skip_move()
            score = self.__negamax_ab(-infinity, infinity, depth)
            self.board.unmake_move()

            if score > best:
                best = score
                best_move = move

        self.board.make_move(best_move)
        duck_move = random.choice(self.board.get_legal_moves())
        self.board.unmake_move()

        return (best, best_move, duck_move)
