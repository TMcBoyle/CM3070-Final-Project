from game_manager import GameManager
from agent import Agent
from goose import Goose
from swan import Swan
from timeit import timeit

import cProfile as cpr
import pstats as ps

def main():
    Swan.train_iterative("models/swan_v8_gen9", "models/swan_v9", 10, 30)
    #gm = GameManager(Swan("models/swan_v8_gen9"), Swan("models/swan"), "game", False, True)
    #gm.play_games(100)

if __name__ == "__main__":
    main()
