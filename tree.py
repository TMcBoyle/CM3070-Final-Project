import copy
from chess import board

class Node:
    def __init__(self, state: board.Board, parent: "Node"=None):
        self.state = state
        self.parent = parent
        self.children = {}
    
    def expand(self):
        """ Expands this node by creating a child node for all possible legal
            moves from this position, if this hasn't already been done.
        """
        if self.children:
            return
        
        moves = self.state.get_legal_moves()
        for move in moves:
            child_state = copy.deepcopy(self.state)
            child_state.make_move(move)
            self.children[str(move)] = Node(child_state, parent=self)

    def count(self):
        """ Counts the number of child nodes this node has, and the number of their children.
        """
        result = len(self.children)
        for _, child in self.children.items():
            result += child.count()
        return result

class Tree:
    def __init__(self, root=board.Board()):
        self.root = Node(root)

    def grow(self, depth=1):
        """ Recursively grows this tree up to the provided depth.
        """
        leaves = [self.root]
        while depth > 0 and leaves:
            new_leaves = []
            while leaves:
                current = leaves.pop()
                current.expand()
                new_leaves += current.children.values()
            leaves += new_leaves
            depth -= 1

    def size(self):
        return self.root.count()
