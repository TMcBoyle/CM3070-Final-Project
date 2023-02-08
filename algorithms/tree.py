""" Tree/Node classes
"""
class Node:
    """ Represents a node in the game tree. Each node stores the most
        recent move made to reach that point, and its parent/children.
    """
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.children = []

    def add_children(self, children: list):
        for child in children:
            self.children.append(Node(child, self))
