from chess.board import Board
import random

class Agent:
    def __init__(self):
        self.board = Board()

    def get_next_move(self):
        legal_moves = self.board.generate_moves()
        if legal_moves:
            move = random.choice(legal_moves)
            self.board.make_move(move)

            duck_moves = self.board.generate_moves()
            duck = random.choice(duck_moves)
            self.board.make_move(duck)

            return (None, move, duck)
        else:
            return None

    def play_move(self, move):
        self.board.make_move(move)
