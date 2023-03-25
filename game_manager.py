from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType
from agent import Agent

from random import randint

class GameManager:
    def __init__(self, player_one: Agent, player_two: Agent):
        self.board: Board = None
        self.players = [player_one, player_two]

    def tournament(players: list[Agent], games_per_round: int, output: str):
        """ Plays a tournament between a list of players.
        """
        results = {}
        while players:
            player = players.pop()
            results[str(player)] = {}
            for opponent in players:
                gm = GameManager(player, opponent)
                results[str(player)][str(opponent)] = gm.play_games(games_per_round, output, True)
        
        with open("results.txt", "w") as file:
            for result in results.items():
                file.write(f"{result}\n")        

    def play_games(self, games: int, output: str, alternate_sides: bool=True):
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

                if output == "move":
                    print(f"{move[0]}{move[1]}")

                current_player = 1 - current_player

            if board.game_state == GameState.WHITE_WINS:
                score[white_idx] += 1
            elif board.game_state == GameState.BLACK_WINS:
                score[1 - white_idx] += 1
            else:
                score[0] += 0.5
                score[1] += 0.5

            if output in ("move", "game"):
                print(f"Game {n} over: {board.game_state._name_}, Current score: {self.players[0]} {score[0]} - {self.players[1]} {score[1]}")
                
            if alternate_sides:
                white_idx = 1 - white_idx
        
        if output in ("move", "game", "match"):
            print(f"Match over: {self.players[0]} {score[0]} - {self.players[1]} {score[1]}")

        return score
