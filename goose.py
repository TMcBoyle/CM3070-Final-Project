from chess.board import Board
from tree import Tree

import random

class Goose:
    def __init__(self, game_tree=Tree()):
        self.game_tree = game_tree
        self.current = self.game_tree.root
    
    def play(self):
        move = self.select_move()
        self.apply_move(move)

        return move

    def apply_move(self, move: str):
        self.current.expand()
        self.current = self.current.children[move]

    def select_move(self):
        self.current.expand()

        best = { 'move': None, 'score': 0}
        for move, node in self.current.children.items():
            score = self.evaluate(node.state)
            if score > best['score']:
                best['move'] = move
                best['score'] = score
        return best['move']

    def evaluate(self, position: Board):
        return random.random()
