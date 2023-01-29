from chess import board
import random

class Agent:
    def evaluate(self, board: board.Board):
        legal_moves = board.get_legal_moves()
        return random.choice(legal_moves)
