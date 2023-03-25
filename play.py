""" Script for playing a game against a provided agent.
"""
import sys

from chess.board import Board, GameState
from chess.sides import Side
from chess.moves import Move, MoveType

from agent import Agent
from swan import Swan
from goose_v3 import Goose

def play(player_side: str, agent: Agent):
    player_side = \
        (Side.WHITE, Side.WHITE_DUCK) if player_side.upper() == "WHITE" \
        else (Side.BLACK, Side.BLACK_DUCK)
    board = Board()
    agent.reset()

    while board.game_state == GameState.ONGOING:
        if board.turn in player_side:
            move = input("Play a move (e.g., e2e4@g5):\n")
            piece_move = Move.from_string(move[:-3], MoveType.MANUAL)
            duck_move = Move.from_string(move[-3:], MoveType.DUCK)
        else:
            move = agent.get_next_move()
            piece_move = move[1]
            duck_move = move[2]
            print(f"{agent} plays {piece_move}{duck_move}...")

        board.make_move(piece_move)
        board.make_move(duck_move)
        agent.play_move(piece_move)
        agent.play_move(duck_move)

    print(f"Game over! {board.game_state._name_}")

if __name__ == "__main__":
    player_side = sys.argv[1]
    target_engine = sys.argv[2]
    if target_engine.upper() == "AGENT":
        play(player_side, Agent())
    elif target_engine.upper() == "SWAN":
        play(player_side, Swan('models/swan_v9_gen9'))
    elif target_engine.upper() == "GOOSE":
        play(player_side, Goose())
    else:
        print("python play.py [white|black] [agent|swan|goose]")
