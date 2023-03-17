""" 'Swan' - a chess engine using a machine learning approach.
"""
from chess.board import Board, GameState
from chess.moves import Move, MoveType
from chess.sides import Side, opposing_side
from chess.pieces import PieceType

from agent import Agent
from chess import consts
from chess.search.algorithms import alpha_beta
from chess.search.node import Node

import random
import numpy as np
import tensorflow as tf
from math import inf as infinity

def bitboard_to_list(board: int):
    return np.array([
        [(x & 2**n) for n in range(8)] for x in board.to_bytes(8, "big")
    ])

class Swan(Agent):
    def __init__(self, model_path: str=None):
        self.board:     Board = Board()
        self.eval_side: Side  = None
        self.root:      Node  = Node()
        self.current:   Node  = self.root

        if model_path:
            self.model = tf.keras.models.load_model("model_path")
        else:    
            self.model = Swan.build_model()

    def build_model():
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Input(shape=(18, 8, 8)))
        model.add(tf.keras.layers.Convolution2D(8, (3, 3), activation="relu"))
        model.add(tf.keras.layers.GlobalAveragePooling2D())
        model.add(tf.keras.layers.Dense(8, activation="relu"))
        model.add(tf.keras.layers.Dense(4, activation="sigmoid"))
        model.add(tf.keras.layers.Dense(2, activation="softmax"))
        return model

    def save_model(self, model_path: str):
        self.model.save(model_path)

    def generate_training_data(n: int, model_path: str=None):
        """ Generates training data for Swan's neural network. This is done
            by self-playing n games with a search depth of 1 (for quick
            game generation). Certain positions from the game are stored along
            with the final score of the position (1 if white wins, 0 if black wins).
        """
        agent = Swan(model_path)

        saved_positions = []
        for _ in range(n):
            board = Board()
            while board.game_state == GameState.ONGOING:
                moves = agent.search(1)

                board.make_move(moves[1])
                board.make_move(moves[2])

                agent.play_move(moves[1])
                agent.play_move(moves[2])

    def train(self, games: int, save_path=None):
        """ Trains Swan's neural network.
        """
        for _ in range(games):
            pass

        if save_path:
            tf.keras.models.save_model(save_path)

    def evaluate(board: Board, **kwargs: dict):
        model = kwargs['model']
        data = []
        for b in board.boards.pieces[Side.WHITE].values():
            data.append(bitboard_to_list(b))
        for b in board.boards.pieces[Side.BLACK].values():
            data.append(bitboard_to_list(b))
        data.append(bitboard_to_list(board.boards.white))
        data.append(bitboard_to_list(board.boards.black))
        data.append(bitboard_to_list(board.boards.duck))
        data.append(bitboard_to_list(board.boards.occupied))
        data.append(bitboard_to_list(board.castle_rights))
        data.append(bitboard_to_list(board.en_passant))
        data = np.array(data)

        eval_idx = 0 if board.turn == Side.WHITE else 1
        return model(np.expand_dims(data, axis=0))[0][eval_idx]

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
        
    def search(self, depth: int=1):
        self.eval_side = self.board.turn
        result = alpha_beta(self.board, self.current, depth, Swan.evaluate, model=self.model)

        return (self.current.score, result[0], result[1])
