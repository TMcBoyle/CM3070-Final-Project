""" Search algorithms """
from chess.board import Board
from chess.moves import Move

class Node:
    def __init__(self, board: Board, move: Move=None, parent: "Move"=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = []

    def expand(self):
        if not self.children:
            for move in self.board.get_legal_moves():
                self.children.append(Node(self.board, move, self))

class Tree:
    def __init__(self, board: Board):
        self.board = board
        self.root = Node(self.board)
