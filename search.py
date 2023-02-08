""" Search algorithms """
from chess.board import Board
from chess.moves import Move

class Node:
    def __init__(self, move: Move=None, parent: "Move"=None):
        self.move = move
        self.parent = parent
        self.children = []

class Tree:
    def __init__(self, board: Board):
        self.board = board
        self.root = Node()

    def grow(self, node: Node, depth=1):
        current = node
        if depth > 0:
            if not current.children:
                for move in self.board.get_legal_moves():
                    current.children.append(Node(move, current))
            for child in current.children:
                self.board.make_move(child.move)
                self.grow(child, depth - 1)
                self.board.unmake_move()
