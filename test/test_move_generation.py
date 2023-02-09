""" Move generation unit tests """
import unittest
from chess.board import Board
from chess.moves import Move

class TestMoveGeneration(unittest.TestCase):
    def test_starting_position(self):
        board = Board()
        moves = board.get_legal_moves()        
        self.assertEqual(len(moves), 20)

    def test_pawn_moves(self):
        board = Board.from_fen_string("1k6/8/8/5pp1/4pPP1/1PpP4/P1P1P3/1K6 w - - 0 1")
        moves = board.get_legal_moves()
        moves.sort(key=lambda m: (m.from_index, m.to_index))

        expected = [
            # Pawn moves
            Move.from_string("a2a3"),
            Move.from_string("a2a4"),
            Move.from_string("b3b4"),
            Move.from_string("d3e4"),
            Move.from_string("d3d4"),
            Move.from_string("e2e3"),
            Move.from_string("f4g5"),
            Move.from_string("g4f5"),
            # King moves
            Move.from_string("b1a1"),
            Move.from_string("b1b2"),
            Move.from_string("b1c1"),
        ]
        expected.sort(key=lambda m: (m.from_index, m.to_index))

        self.assertListEqual(moves, expected)
