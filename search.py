""" Search algorithms """
from chess.board import Board
from chess.moves import Move
from math import inf as infinity

class Node:
    def __init__(self, move: Move=None, parent: "Move"=None):
        self.move = move
        self.score = -infinity
        self.parent = parent
        self.children = []

    def expand(self, moves: list[Move]):
        for move in moves:
            self.children.append(Node(move, self))

    def as_string(node, depth=0):
        result = " " * depth + f"{str(node.move)} ({node.score})"
        for child in node.children:
            result += "\n" + Node.as_string(child, depth + 1)
        return result

    def __gt__(self, other: "Node"):
        try:
            return self.score > other.score
        except:
            raise NotImplemented
        
    def __lt__(self, other: "Node"):
        try:
            return self.score < other.score
        except:
            raise NotImplemented

    def __str__(self):
        return Node.as_string(self, 0)
