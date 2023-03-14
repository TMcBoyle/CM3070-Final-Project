""" Algorithm unit tests """
import unittest
from chess.board import Board, GameState
from agent import Agent
from goose import Goose
from swan import Swan
from chess import utils
from chess import squares
from chess import consts

import random

class TestAgents(unittest.TestCase):
    def test_random_agent(self):
        agent = Agent()
        board = Board()
        while board.game_state == GameState.ONGOING:
            moves = agent.get_next_move()
            
            agent.play_move(moves[1])
            agent.play_move(moves[2])

            board.make_move(moves[1])
            board.make_move(moves[2])

    def test_traditional_agent(self):
        agent = Goose()
        board = Board()
        while board.game_state == GameState.ONGOING:
            moves = agent.get_next_move()

            agent.play_move(moves[1])
            agent.play_move(moves[2])
            
            board.make_move(moves[1])
            board.make_move(moves[2])

            self.assertListEqual(
                agent.board.mailbox,
                agent.board.recalculate_mailbox()
            )

            self.assertListEqual(
                board.mailbox,
                board.recalculate_mailbox()
            )

    def test_machine_learning_agent(self):
        agent = Swan()
        board = Board()
        while board.game_state == GameState.ONGOING:
            moves = agent.get_next_move()

            agent.play_move(moves[1])
            agent.play_move(moves[2])
            
            board.make_move(moves[1])
            board.make_move(moves[2])

            self.assertListEqual(
                agent.board.mailbox,
                agent.board.recalculate_mailbox()
            )

            self.assertListEqual(
                board.mailbox,
                board.recalculate_mailbox()
            )
