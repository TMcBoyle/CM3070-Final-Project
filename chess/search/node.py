""" Search algorithms """
from chess.board import Board
from chess.moves import Move
from math import inf as infinity
from random import choice
from enum import IntEnum

class NodeType(IntEnum):
    """ Node Types as described by Tony Marshland and Fred Popowich
        https://webdocs.cs.ualberta.ca/~tony/OldPapers/parallel.pdf
    """
    UNKNOWN = -1
    PV  = 0 # Principal variation - the "main" moves
    CUT = 1 # Cut nodes - nodes that failed a beta check
    ALL = 2 # All nodes - nodes that failed an alpha check
    
class Node:
    def __init__(self, move: Move=None, parent: "Node"=None):
        self.move = move
        self.parent = parent

        self.node_type = NodeType.UNKNOWN
        self.zbr = None
        self.best_move = None
        self.search_depth = 0
        self.score = -infinity

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
