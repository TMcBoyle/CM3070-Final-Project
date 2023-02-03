from game_manager import GameManager
from agent import Agent
from timeit import timeit

def main():
    gm = GameManager(Agent(), Agent(), output=False)
    gm.start(10)

if __name__ == "__main__":
    main()
