""" Zobrist hashing unit tests """
import unittest
from chess.board import Board
from goose import Goose
from chess.search.node import *
from chess.search.algorithms import *
from random import random
import time

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.start = time.time()

    def tearDown(self):
        running_time = time.time() - self.start
        print(f"Test running time: {running_time}")

    def test_minimax(self):
        # Test basic minimax search to some depth
        board = Board()
        root = Node()

        minimax(board, root, Goose.evaluate, 4)

    def test_alpha_beta(self):
        # Test alpha-beta minimax search to some depth
        board = Board()
        root = Node()

        alpha_beta(board, root, {}, Goose.evaluate)
