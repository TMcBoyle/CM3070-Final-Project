""" Search algorithms """
from chess.board import Board
from chess.moves import Move

class Node:
    def __init__(self, move: Move=None, parent: "Move"=None):
        self.move = move
        self.parent = parent
        self.children = []

    def expand(self, nodes: list["Node"]):
        self.children = nodes

class Tree:
    def __init__(self, board: Board):
        self.board = board
        self.root = Node(self.board)
        self.current = self.root
