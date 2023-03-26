""" Demo script for project video.
"""
from game_manager import GameManager
from goose_v3 import Goose
from swan import Swan

def demo():
    gm = GameManager(Goose(), Swan("models/swan_v9_gen9"))
    gm.play_games(1, "move", False)

if __name__ == "__main__":
    demo()
