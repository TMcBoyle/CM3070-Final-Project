from chess.board import Board
import random

class Agent:
    def __init__(self, board: Board):
        self.board = board

    def get_next_move(self):
        legal_moves = self.board.get_legal_moves()
        if legal_moves:
            move = random.choice(legal_moves)
            self.board.make_move(move)

            duck_moves = self.board.get_legal_moves()
            duck = random.choice(duck_moves)
            self.board.unmake_move()

            return (move, duck)
        else:
            return None
