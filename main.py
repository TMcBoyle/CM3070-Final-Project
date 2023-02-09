from game_manager import GameManager
from agent import Agent
from goose import Goose
from timeit import timeit

def main():
    gm = GameManager(Goose, Agent, output="outcome", save_games=False)
    gm.start(100)

if __name__ == "__main__":
    print(timeit(main, number=1))
