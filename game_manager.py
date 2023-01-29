from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

class GameManager:
    def __init__(self, white: Agent=None, black: Agent=None):
        self.board = Board()
        self.white = white
        self.black = black
    
    def start(self):
        while self.board.terminal == GameState.ONGOING:
            move = self.request_next_move()
            self.board.make_move(move)
            duck = self.request_next_move()
            self.board.make_move(duck)
            print(f"{move}{duck} was played.")
            self.board.check_game_end()
        if self.board.terminal == GameState.WHITE_WINS:
            result = "White wins!"
        elif self.board.terminal == GameState.BLACK_WINS:
            result = "Black wins!"
        print(f"Game over. {result}")

    def request_next_move(self):
        legal_moves = self.board.get_legal_moves()

        if self.board.turn == Side.WHITE and not self.board.duck_turn:
            if self.white:
                move = self.white.evaluate(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("White to move: "))
                return move
        elif self.board.turn == Side.WHITE and self.board.duck_turn:
            if self.white:
                move = self.white.evaluate(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("White to place the duck: "), move_type=MoveType.DUCK)
                return move
        elif self.board.turn == Side.BLACK:
            if self.black:
                move = self.black.evaluate(self.board)
                return move
            else: 
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("Black to move: "))
                return move
        elif self.board.turn == Side.BLACK and self.board.duck_turn:
            if self.black:
                move = self.black.evaluate(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("Black to place the duck: "), move_type=MoveType.DUCK)
                return move
