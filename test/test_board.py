import unittest
from chess.board import Board
from chess.moves import Move, MoveType

class TestBoard(unittest.TestCase):
    def test_string_loading(self):
        board = Board()
        fenboard = Board.from_fen_string("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        self.assertEqual(board.zbr, fenboard.zbr)

        board.skip_move()
        fenboard = Board.from_fen_string("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w@ KQkq - 0 1")
        self.assertEqual(board.zbr, fenboard.zbr)

        board.skip_move()
        board.make_move(Move.from_string("e7e5"))
        fenboard = Board.from_fen_string("rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR b@ KQkq - 0 1")

        print(board)
        print(fenboard)
        self.assertEqual(board.zbr, fenboard.zbr)
