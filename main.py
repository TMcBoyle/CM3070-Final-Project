from game_manager import GameManager
from agent import Agent

def main():
    gm = GameManager(Agent(), Agent())
    gm.start()

if __name__ == "__main__":
    main()
