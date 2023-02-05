from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

from random import randint

class GameManager:
    def __init__(self, player_one: Agent=None, player_two: Agent=None, output: bool=True):
        self.board = None
        self.players = [player_one, player_two]
        self.output = output

        self.order = randint(0, 1)
    
    def start(self, games=1):
        scores = [0, 0]

        for _ in range(games):
            self.white = self.players[self.order]
            self.black = self.players[1 - self.order]

            self.board = Board()
            while self.board.terminal == GameState.ONGOING:
                move = self.request_next_move()
                self.board.make_move(move)
                duck = self.request_next_move()
                self.board.make_move(duck)
                if self.output == "verbose":
                    print(f"{move}{duck} was played.")
                self.board.check_game_end()
            if self.board.terminal == GameState.WHITE_WINS:
                result = "White wins!"
                scores[self.order] += 1
            elif self.board.terminal == GameState.BLACK_WINS:
                result = "Black wins!"
                scores[1 - self.order] += 1
            elif self.board.terminal == GameState.STALEMATE:
                result = "Stalemate, that's quackers!"
                scores[0] += 0.5
                scores[1] += 0.5

            self.order = 1 - self.order

            if self.output == "verbose":
                print(f"Game over. {result}")
        if self.output in ("verbose", "outcome"):
            print(f"Match over. Final score: {scores[0]}-{scores[1]}")

    def request_next_move(self):
        legal_moves = self.board.get_legal_moves()

        if self.board.turn == Side.WHITE and not self.board.duck_turn:
            if self.white:
                move = self.white.get_next_move(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("White to move: "))
                return move
        elif self.board.turn == Side.WHITE and self.board.duck_turn:
            if self.white:
                move = self.white.get_next_move(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("White to place the duck: "), move_type=MoveType.DUCK)
                return move
        elif self.board.turn == Side.BLACK:
            if self.black:
                move = self.black.get_next_move(self.board)
                return move
            else: 
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("Black to move: "))
                return move
        elif self.board.turn == Side.BLACK and self.board.duck_turn:
            if self.black:
                move = self.black.get_next_move(self.board)
                return move
            else:
                move = None
                while move not in legal_moves:
                    move = Move(algebraic=input("Black to place the duck: "), move_type=MoveType.DUCK)
                return move
