""" Functions for the minimax algorithm. Implementation is based
    on https://www.chessprogramming.org/Minimax#Implementation.
"""
from .tree import Node
from chess.board import Board

def __min(board: Board, depth: int, eval_fn: function):
    if depth == 0:
        return eval_fn(board)
    
    minimum = None
    for move in board.get_legal_moves():
        board.make_move(move)
        for duck_move in board.get_duck_moves():
            board.make_move(duck_move)
            score = __max(board, depth - 1, eval_fn)
            if minimum is None or score < minimum:
                minimum = score
            
    return minimum

def __max(board: Board, depth: int, eval_fn: function):
    if depth == 0:
        return eval_fn(board)
    
    maximum = None
    for move in board.get_legal_moves():
        board.make_move(move)
        for duck_move in board.get_duck_moves():
            board.make_move(duck_move)
            score = __min(board, depth - 1, eval_fn)
            if maximum is None or score > maximum:
                maximum = score
    return maximum

def minimax(board: Board, depth: int, eval_fn: function):
    pass
