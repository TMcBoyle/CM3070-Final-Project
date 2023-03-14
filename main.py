from game_manager import GameManager
from agent import Agent
from goose import Goose
from swan import Swan
from timeit import timeit

import cProfile as cpr
import pstats as ps

def main():
    gm = GameManager(Goose, Agent, output="outcome", save_games=True, random_order=True)
    gm.start(100)

if __name__ == "__main__":
    p = cpr.run('main()', './profiling')
    s = ps.Stats("./profiling")
    s.sort_stats(ps.SortKey.TIME)
    s.print_stats(20)
