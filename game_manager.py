from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

from random import randint

class GameManager:
    def __init__(self, player_one: Agent, player_two: Agent, output: str, save_games: bool=False, alternate_sides: bool=True):
        self.board: Board = None
        self.players = [player_one, player_two]
        self.output = output
        self.save_games = save_games
        self.alternate_sides = alternate_sides

    def play_games(self, games: int):
        """ Plays a number of games between player_one and player_two.
        """
        score = [0, 0]
        white_idx = 0
        for n in range(games):
            board = Board()
            white = self.players[white_idx]
            white.reset()
            black = self.players[1 - white_idx]
            black.reset()

            current_player = white_idx
            while board.game_state == GameState.ONGOING:
                move = self.players[current_player].get_next_move()[1:]
                board.make_move(move[0])
                board.make_move(move[1])
                white.play_move(move[0])
                white.play_move(move[1])
                black.play_move(move[0])
                black.play_move(move[1])

                if self.output == "move":
                    print(f"{move[0]}{move[1]}")

                current_player = 1 - current_player

            if board.game_state == GameState.WHITE_WINS:
                score[white_idx] += 1
            elif board.game_state == GameState.BLACK_WINS:
                score[1 - white_idx] += 1
            else:
                score[0] += 0.5
                score[1] += 0.5

            if self.output in ("move", "game"):
                print(f"Game {n} over: {board.game_state._name_}, Current score: {self.players[0]} {score[0]} - {self.players[1]} {score[1]}")
                
            if self.alternate_sides:
                white_idx = 1 - white_idx
        
        if self.output in ("move", "game", "match"):
            print(f"Match over: {self.players[0]} {score[0]} - {self.players[1]} {score[1]}")

        return score
