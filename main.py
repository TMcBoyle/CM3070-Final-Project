from game_manager import GameManager
from agent import Agent
from timeit import timeit

def main():
    gm = GameManager(Agent(), Agent(), output="outcome")
    gm.start(100)

if __name__ == "__main__":
    print(timeit(main, number=1))
