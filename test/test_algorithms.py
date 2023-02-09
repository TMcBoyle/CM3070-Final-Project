""" Algorithm unit tests """
import unittest
from chess import utils
from chess import squares
from chess import consts

import random

class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        self.random = random.Random(1189998819991197253)

    def test_get_file(self):
        for idx, square in enumerate(squares.labels):
            file = "abcdefgh".index(square[0])
            self.assertEqual(utils.get_file(idx), consts.LOOKUP_FILE[file])

    def test_get_rank(self):
        for idx, square in enumerate(squares.labels):
            rank = "12345678".index(square[1])
            self.assertEqual(utils.get_rank(idx), consts.LOOKUP_RANK[rank])

    def test_get_diagonal(self):
        for idx, _ in enumerate(squares.labels):
            mask = squares.masks[idx]
            self.assertTrue(utils.get_diagonal(idx) & mask)

    def test_get_antidiagonal(self):
        for idx, _ in enumerate(squares.labels):
            mask = squares.masks[idx]
            self.assertTrue(utils.get_antidiagonal(idx) & mask)

    def test_get_squares(self):
        white_pieces = consts.INIT_WHITE_PIECES
        squares = utils.get_squares(white_pieces)
        self.assertTrue(all(
            s in range(0, 16) for s in squares
        ))

        black_pieces = consts.INIT_BLACK_PIECES
        squares = utils.get_squares(black_pieces)
        self.assertTrue(all(
            s in range(48, 64) for s in squares
        ))

    def test_invert(self):
        normal = [self.random.randint(0, 2**64-1) for n in range(100)]
        for n in normal:
            invert = utils.invert(n)
            self.assertEqual(n & invert, consts.EMPTY)
            self.assertEqual(n ^ invert, consts.FILLED)

    def test_delta_swap(self):
        board = 0b10010100
        mask  = 0b01010101
        delta = 1
        self.assertEqual(utils.delta_swap(board, mask, delta), 0b01101000)

    def test_translations(self):
        board = squares.masks[squares.e4]
        board = utils.north(board, 1)
        self.assertEqual(board, squares.masks[squares.e5])
        board = utils.west(board, 3)
        self.assertEqual(board, squares.masks[squares.b5])
        board = utils.east(board, 6)
        self.assertEqual(board, squares.masks[squares.h5])
        board = utils.south(board, 4)
        self.assertEqual(board, squares.masks[squares.h1])
        board = utils.east(board, 1)
        self.assertEqual(board, consts.EMPTY)

    def test_flip_vertical(self):
        board = consts.TEST_UPPER_LEFT
        self.assertEqual(utils.flip_vertical(board), consts.TEST_LOWER_LEFT)
        board = consts.TEST_UPPER_RIGHT
        self.assertEqual(utils.flip_vertical(board), consts.TEST_LOWER_RIGHT)
        board = consts.TEST_LOWER_LEFT
        self.assertEqual(utils.flip_vertical(board), consts.TEST_UPPER_LEFT)
        board = consts.TEST_LOWER_RIGHT
        self.assertEqual(utils.flip_vertical(board), consts.TEST_UPPER_RIGHT)

    def test_flip_horizontal(self):
        board = consts.TEST_UPPER_LEFT
        self.assertEqual(utils.flip_horizontal(board), consts.TEST_UPPER_RIGHT)
        board = consts.TEST_UPPER_RIGHT
        self.assertEqual(utils.flip_horizontal(board), consts.TEST_UPPER_LEFT)
        board = consts.TEST_LOWER_LEFT
        self.assertEqual(utils.flip_horizontal(board), consts.TEST_LOWER_RIGHT)
        board = consts.TEST_LOWER_RIGHT
        self.assertEqual(utils.flip_horizontal(board), consts.TEST_LOWER_LEFT)

    def test_flip_diagonal_a1h8(self):
        board = consts.TEST_UPPER_LEFT
        self.assertEqual(utils.flip_diagonal_a1h8(board), consts.TEST_LOWER_RIGHT)
        board = consts.TEST_LOWER_LEFT
        self.assertEqual(utils.flip_diagonal_a1h8(board), consts.TEST_LOWER_LEFT)

    def test_flip_diagonal_a8h1(self):
        board = consts.TEST_UPPER_LEFT
        self.assertEqual(utils.flip_diagonal_a8h1(board), consts.TEST_UPPER_LEFT)
        board = consts.TEST_LOWER_LEFT
        self.assertEqual(utils.flip_diagonal_a8h1(board), consts.TEST_UPPER_RIGHT)

    def test_rotations(self):
        board = consts.TEST_UPPER_LEFT
        self.assertEqual(utils.rotate_90(board), consts.TEST_UPPER_RIGHT)
        self.assertEqual(utils.rotate_180(board), consts.TEST_LOWER_RIGHT)
        self.assertEqual(utils.rotate_270(board), consts.TEST_LOWER_LEFT)

    def test_hyperbola_quintessence(self):
        idx = squares.e3
        piece = squares.masks[idx]
        other_pieces = [squares.f2, squares.b3, squares.h6]
        occupancy = piece
        for other in other_pieces:
            occupancy |= squares.masks[other]
        # Horizontal

        # Diagonal
        expected = consts.EMPTY
        for square in [
            squares.d4, squares.c5, squares.b6, squares.a7, # UL diagonal
            squares.f4, squares.g5, squares.h6, # UR diagonal
            squares.d2, squares.c1, # DL diagonal
            squares.f2 # DR diagonal
        ]:
            expected |= squares.masks[square]

        diag = utils.hyperbola_quintessence(occupancy, utils.get_diagonal(idx), piece)
        anti = utils.hyperbola_quintessence(occupancy, utils.get_antidiagonal(idx), piece)
        result = diag | anti

        print("")
        utils.pretty_print(diag)
        print("")
        utils.pretty_print(expected)

        self.assertEqual(result, expected)
