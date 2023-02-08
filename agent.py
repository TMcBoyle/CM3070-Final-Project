from chess import board
import random

class Agent:
    def get_next_move(self, board: board.Board):
        legal_moves = board.get_legal_moves()
        if legal_moves:
            return random.choice(legal_moves)
        else:
            print(board)
            print(board.get_legal_moves())
            return None
