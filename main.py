from chess.board import Board
from chess import *

def main():
    pretty_print(flip_diagonal_a1h8(TEST_R_SHAPE))
    print("")
    pretty_print(flip_diagonal_a8h1(TEST_R_SHAPE))

if __name__ == "__main__":
    main()
