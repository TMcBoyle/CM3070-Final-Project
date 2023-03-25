""" 'Swan' - a chess engine using a machine learning approach.
"""
from chess.board import Board, GameState
from chess.moves import Move, MoveType
from chess.sides import Side, opposing_side
from chess.pieces import PieceType

from agent import Agent
from chess import consts
from chess.search.algorithms import alpha_beta_nn
from chess.search.node import Node
from game_manager import GameManager

import random
import numpy as np
import tensorflow as tf
from bitarray.util import int2ba
from math import inf as infinity

def bitboard_to_list(board: int):
    return np.reshape(int2ba(board, length=64, endian='big').tolist(), (8, 8))

class Swan(Agent):
    def __init__(self, model_path: str=None):
        self.board:     Board = Board()
        self.eval_side: Side  = None
        self.root:      Node  = Node()
        self.current:   Node  = self.root
        self.model_path = model_path

        if model_path:
            self.model = tf.keras.models.load_model(model_path, compile=False)
        else:    
            self.model = Swan.build_model()

    def build_model():
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Input(shape=(18, 8, 8)))
        model.add(tf.keras.layers.Convolution2D(8, (3, 3), activation="relu"))
        model.add(tf.keras.layers.GlobalAveragePooling2D())
        model.add(tf.keras.layers.Dense(32, activation="relu"))
        model.add(tf.keras.layers.Dense(16, activation="sigmoid"))
        model.add(tf.keras.layers.Dense(2, activation="softmax"))
        return model

    def save_model(self, model_path: str):
        self.model.save(model_path)

    def generate_training_data(n: int, model_path: str=None, output_file: str=None):
        """ Generates training data for Swan's neural network. This is done
            by self-playing n games with a search depth of 1 (for quick
            game generation). All game positions are stored along with the final
            score of the position (1 if white wins, 0 if black wins).
        """
        saved_positions = []
        for i in range(n):
            print(f"Generating training data, game {i}...")
            new_positions = []

            agent = Swan(model_path)
            board = Board()

            ply = 0
            while board.game_state == GameState.ONGOING:
                moves = agent.search(1)

                board.make_move(moves[1])
                board.make_move(moves[2])

                agent.play_move(moves[1])
                agent.play_move(moves[2])

                if ply > 6: # It's not useful to save the first few positions to prevent overfitting
                    new_positions.append(board.to_fen_string())
                ply += 1

            expected_score = \
                     (1.0, 0.0) if board.game_state == GameState.WHITE_WINS \
                else (0.5, 0.5) if board.game_state == GameState.STALEMATE \
                else (0.0, 1.0)
            
            saved_positions += [(p, expected_score) for p in new_positions]
            print(f"Game {i} completed, {len(new_positions)} positions generated.")
        
        if output_file:
            with open(output_file, "w") as file:
                for position in saved_positions:
                    file.write(str(position) + '\n')

    def train(training_data_path: str, model_path=None, out_model_path=None):
        """ Trains Swan's neural network.
        """
        raw_training_data = []
        with open(training_data_path, "r") as file:
            for line in file:
                raw_training_data.append(eval(line))

        training_inputs = []
        training_outputs = []
        test_inputs = []
        test_outputs = []
        for record in raw_training_data:
            board = Board.from_fen_string(record[0])
            if random.random() > 0.2:
                training_inputs.append(Swan.build_model_input(board))
                training_outputs.append(record[1])
            else:
                test_inputs.append(Swan.build_model_input(board))
                test_outputs.append(record[1])

        print("Beginning training run...")
        agent = Swan(model_path)
        agent.model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])
        history = agent.model.fit(np.array(training_inputs), np.array(training_outputs), epochs=30, batch_size=32, validation_split=0.1)
        loss, accuracy = agent.model.evaluate(np.array(test_inputs), np.array(test_outputs))
        print(f"Training run complete - Loss: {loss}, Accuracy: {accuracy}")
        agent.save_model(out_model_path)

    def train_iterative(starting_model_path: str, output_prefix: str, generations: int, training_games_per_gen: int):
        previous_model_path = starting_model_path
        model_path = starting_model_path
        for g in range(generations):
            print(f"Training generation {g}")
            score = [0, 1]
            out_model_path = f"{output_prefix}_gen{g}"
            training_path = f"training_sets/{output_prefix}_gen{g}"
            rounds = 0
            while (score[0] / (score[0] + score[1])) < 0.55:
                Swan.generate_training_data(training_games_per_gen, model_path, training_path)
                Swan.train(training_path, model_path, f"{out_model_path}")
                score = Swan.compare_models(f"{out_model_path}", previous_model_path, 30)
                print(f"Generation {g} round {rounds} completed. Score: {score}")
                model_path = out_model_path
                rounds += 1

            model_path = out_model_path
            previous_model_path = model_path
            print(f"Completed generation {g}")

    def compare_models(model_a_path: str, model_b_path: str, games: int):
        """ Compares two models by playing a number of games and returning
            the result.
        """
        model_a = Swan(model_a_path)
        model_b = Swan(model_b_path)

        gm = GameManager(model_a, model_b, "game")
        result = gm.play_games(games)
        return result

    def build_model_input(board: Board):
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
        return data

    def evaluate(board: Board, **kwargs: dict):
        model = kwargs['model']
        data = Swan.build_model_input(board)

        return model(np.array([data]))[0]

    def reset(self):
        self.board:     Board = Board()
        self.eval_side: Side  = None
        self.root:      Node  = Node()
        self.current:   Node  = self.root

    def get_next_move(self):
        return self.search(2)

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
        result = alpha_beta_nn(self.board, self.current, depth, Swan.evaluate, model=self.model)

        return (self.current.score, result[0], result[1])

    def __str__(self):
        return f"<Swan model_path: {self.model_path}>"
