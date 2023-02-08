from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

from random import randint

class GameManager:
    def __init__(self, player_one: type[Agent], player_two: type[Agent], output: bool=True):
        self.board: Board = None
        self.players = [player_one, player_two]
        self.output = output

        self.order = randint(0, 1)
    
    def start(self, games=1):
        scores = [0, 0]

        for _ in range(games):
            self.board = Board()

            self.white = self.players[self.order](self.board)
            self.black = self.players[1 - self.order](self.board)

            while self.board.game_state == GameState.ONGOING:
                if self.output == "verbose":
                    print(self.board)

                move = self.request_next_move()
                self.board.make_move(move[0])
                self.board.make_move(move[1])

                if self.output == "verbose":
                    print(f"{move[0]}{move[1]} was played.")

            if self.board.game_state == GameState.WHITE_WINS:
                result = "White wins!"
                scores[self.order] += 1

            elif self.board.game_state == GameState.BLACK_WINS:
                result = "Black wins!"
                scores[1 - self.order] += 1

            elif self.board.game_state == GameState.STALEMATE:
                result = "Stalemate, that's quackers!"
                scores[0] += 0.5
                scores[1] += 0.5

            self.order = 1 - self.order

            if self.output == "verbose":
                print(f"Game over. {result}")

        if self.output in ("verbose", "outcome"):
            print(f"Match over. Final score: {scores[0]}-{scores[1]}")

    def request_next_move(self):
        if self.board.turn in (Side.WHITE, Side.WHITE_DUCK) and self.white:
            return self.white.get_next_move()
        elif self.board.turn in (Side.BLACK, Side.BLACK_DUCK) and self.black:
            return self.black.get_next_move()
        # A human player is standing in for one or both agents
        else: 
            legal_moves = self.board.get_legal_moves()
            move = None
            while move not in legal_moves:
                move = Move.from_algebraic(input("Enter a move: "))
            self.board.make_move(move)

            duck_moves = self.board.get_legal_moves()
            duck = None
            while duck not in duck_moves:
                duck = Move.from_algebraic(input("Place the duck: "))
            self.board.unmake_move()
            
            return (duck, move)
