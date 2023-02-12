""" Zobrist hashing unit tests """
import unittest
from chess.board import Board
from chess.moves import Move, MoveType
from chess.zobrist import ZbrHash

class TestZobristHashing(unittest.TestCase):
    def test_make_move(self):
        board = Board()
        h = board.zbr_hash.hash

        board.make_move(Move.from_string("e2e4"))
        self.assertNotEqual(board.zbr_hash.hash, h)

    def test_skip_move(self):
        board = Board()
        h = board.zbr_hash.hash

        board.skip_move()
        self.assertNotEqual(board.zbr_hash.hash, h)
        board.skip_move()
        self.assertNotEqual(board.zbr_hash.hash, h)
        board.skip_move()
        self.assertNotEqual(board.zbr_hash.hash, h)
        board.skip_move()
        self.assertEqual(board.zbr_hash.hash, h)

    def test_unmake_move(self):
        board = Board()
        initial_hash = board.zbr_hash.hash

        board.make_move(Move.from_string("e2e4"))
        self.assertNotEqual(board.zbr_hash.hash, initial_hash)
        board.unmake_move()

        self.assertEqual(board.zbr_hash.hash, initial_hash)

    def test_unmake_capture_move(self):
        board = Board.from_fen_string("5rk1/5ppp/3p4/8/2N5/8/5PPP/5RK1 w - - 0 1")
        initial_hash = board.zbr_hash.hash

        board.make_move(Move.from_string("c4d6"))
        self.assertNotEqual(board.zbr_hash.hash, initial_hash)
        board.unmake_move()

        self.assertEqual(board.zbr_hash.hash, initial_hash)

    def test_unmake_promotions(self):
        board = Board.from_fen_string("1r4k1/2P1P3/8/8/8/8/8/6K1 w - - 0 1")
        initial_hash = board.zbr_hash.hash

        # Regular promotion
        board.make_move(Move.from_string("e7e8=R"))
        self.assertNotEqual(board.zbr_hash.hash, initial_hash)
        board.unmake_move()
        self.assertEqual(board.zbr_hash.hash, initial_hash)
        # Capture promotion
        board.make_move(Move.from_string("c7b8=Q"))
        self.assertNotEqual(board.zbr_hash.hash, initial_hash)
        board.unmake_move()
        self.assertEqual(board.zbr_hash.hash, initial_hash)

    def test_transposition(self):
        board_a = Board()
        board_b = Board()

        # Pawns first
        board_a.make_move(Move.from_string("e2e4"))
        board_a.make_move(Move.from_string("@a3"))
        board_a.make_move(Move.from_string("d7d5"))
        board_a.make_move(Move.from_string("@a6"))
        board_a.make_move(Move.from_string("g1f3"))
        board_a.make_move(Move.from_string("@a3"))
        board_a.make_move(Move.from_string("b8c6"))
        board_a.make_move(Move.from_string("@a6"))

        # Knights first
        board_b.make_move(Move.from_string("g1f3"))
        board_b.make_move(Move.from_string("@a3"))
        board_b.make_move(Move.from_string("b8c6"))
        board_b.make_move(Move.from_string("@a6"))
        board_b.make_move(Move.from_string("e2e4"))
        board_b.make_move(Move.from_string("@a3"))
        board_b.make_move(Move.from_string("d7d5"))
        board_b.make_move(Move.from_string("@a6"))

        self.assertEqual(board_a.zbr_hash.hash, board_b.zbr_hash.hash)

    def test_castle_rights(self):
        # All rights
        board_a = Board.from_fen_string("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        # No rights
        board_b = Board.from_fen_string("r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1")

        self.assertNotEqual(board_a.zbr_hash.hash, board_b.zbr_hash.hash)
