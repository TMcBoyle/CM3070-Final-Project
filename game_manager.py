from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

from random import randint

class GameManager:
    def __init__(self, player_one: type[Agent], player_two: type[Agent], output: str, save_games: bool=False, random_order: bool=True):
        self.board: Board = None
        self.players = [player_one, player_two]
        self.output = output
        self.save_games = save_games

        self.white = None
        self.black = None

        if random_order:
            self.order = randint(0, 1)
        else:
            self.order = 0
    
    def start(self, games=1):
        scores = [0, 0]

        for n in range(games):
            moves = []
            self.board = Board()

            if self.players[self.order]:
                self.white = self.players[self.order]()
            if self.players[1 - self.order]:
                self.black = self.players[1 - self.order]()

            while self.board.game_state == GameState.ONGOING:
                if self.output == "board":
                    print(self.board)

                moves.append(self.request_next_move())
                self.update_board(moves[-1][1], moves[-1][2])

                if self.output in ("board", "verbose"):
                    print(f"{moves[-1][1]}{moves[-1][2]} was played (eval {moves[-1][0]}).")

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

            if self.save_games:
                with open(f'games/game{n}.txt', 'w') as f:
                    for n, move in enumerate(moves):
                        f.write(f"{n}. {move[1]}{move[2]} ({move[0]})\n")
                    f.write(f"{result}")

            if self.output in ("board", "verbose"):
                print(f"Game over. {result}")

        if self.output in ("verbose", "outcome"):
            print(f"Match over. Final score: "\
                  f"{self.players[0]} {scores[0]} - "\
                  f"{self.players[1]} {scores[1]}")
        pass

    def update_board(self, move: Move, duck: Move):
        """ Update the board and notify the opponent of the 
            played move.
        """
        # Notify the opposing agent which moves were played
        if self.board.turn in (Side.WHITE, Side.WHITE_DUCK):
            self.black.play_move(move)
            self.black.play_move(duck)
        elif self.board.turn in (Side.BLACK, Side.BLACK_DUCK):
            self.white.play_move(move)
            self.white.play_move(duck)
        
        # Apply the moves to the main board
        self.board.make_move(move)
        self.board.make_move(duck)

    def request_next_move(self):
        if self.board.turn in (Side.WHITE, Side.WHITE_DUCK) and self.white:
            return self.white.get_next_move()
        elif self.board.turn in (Side.BLACK, Side.BLACK_DUCK) and self.black:
            return self.black.get_next_move()
        # A human player is standing in for one or both agents
        else: 
            legal_moves = self.board.generate_moves()
            move = None
            while move not in legal_moves:
                move = Move.from_string(input("Enter a move: "))
            self.board.make_move(move)

            duck_moves = self.board.generate_moves()
            duck = None
            while duck not in duck_moves:
                duck = Move.from_string(input("Place the duck: "))
            self.board.unmake_move()
            
            return (None, move, duck)
