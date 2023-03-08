from .node import Node
from ..board import Board
from ..moves import Move

import random

from math import inf as infinity

def minimax(board: Board, node: Node, eval_fn: callable, depth: int=1) -> Move:
    def __minimax_recursive(node: Node, eval_fn: callable, depth: int=depth-1):
        if depth == 0:
            node.score = eval_fn(board)
            return node.score
        
        if not node.children:
            node.expand(board.generate_moves(pseudo=True))
        
        best_score = -infinity
        for child in node.children:
            board.make_move(child.move)
            board.skip_move()
            child.score = __minimax_recursive(child, eval_fn, depth-1)
            board.unmake_move()

            if child.score > best_score:
                best_score = child.score

        return best_score

    legal_moves = board.generate_moves()
    if not node.children:
        node.expand(legal_moves)

    best_score = -infinity
    best_move = None

    for child in node.children:
        if child.move not in legal_moves:
            continue

        board.make_move(child.move)
        board.skip_move()
        child.score = -__minimax_recursive(child, eval_fn, depth-1)
        board.unmake_move()

        if child.score > best_score:
            best_score = child.score
            best_move = child.move
    
    board.make_move(best_move)
    duck_move = random.choice(board.generate_moves())
    board.make_move(duck_move)

    return (best_score, best_move, duck_move)

def alpha_beta(board: Board, node: Node, eval_fn: callable, depth: int=1) -> Move:
    def __alpha_beta_recursive(
            node: Node, alpha: float, beta: float, eval_fn: callable, depth: int=depth-1
        ):
        if depth == 0:
            node.score = eval_fn(board)
            return node.score
        
        if not node.children:
            node.expand(board.generate_moves(pseudo=True))
        
        for child in node.children:
            board.make_move(child.move)
            board.skip_move()
            child.score = -__alpha_beta_recursive(child, -beta, -alpha, eval_fn, depth-1)
            board.unmake_move()

            if child.score >= beta:
                child.score = beta
                return beta
            elif child.score > alpha:
                alpha = child.score

        node.score = alpha
        return alpha

    legal_moves = board.generate_moves()
    if not node.children:
        node.expand(legal_moves)

    best_score = -infinity
    best_move = None

    for child in node.children:
        if child.move not in legal_moves:
            continue

        board.make_move(child.move)
        board.skip_move()
        child.score = __alpha_beta_recursive(child, -infinity, infinity, eval_fn, depth-1)
        board.unmake_move()

        if child.score > best_score:
            best_score = child.score
            best_move = child.move
    
    board.make_move(best_move)
    duck_move = random.choice(board.generate_moves())
    board.make_move(duck_move)

    return (best_score, best_move, duck_move)

def alpha_beta_iddfs(board: Board, node: Node, eval_fn: callable, depth: int=1) -> Move:
    def __alpha_beta_iddfs_recursive(
            node: Node, alpha: float, beta: float, eval_fn: callable, depth: int=depth-1
        ):
        if depth == 0:
            node.score = eval_fn(board)
            return node.score
        
        if not node.children:
            node.expand(board.generate_moves(pseudo=True))
        
        for child in node.children:
            board.make_move(child.move)
            board.skip_move()
            child.score = -__alpha_beta_iddfs_recursive(
                child, -beta, -alpha, eval_fn, depth-1
            )
            board.unmake_move()

            if child.score >= beta:
                child.score = beta
                return beta
            elif child.score > alpha:
                alpha = child.score

        node.score = alpha
        return alpha

    legal_moves = board.generate_moves()
    if not node.children:
        node.expand(legal_moves)

    best_score = -infinity
    best_move = None

    for child in node.children:
        if child.move not in legal_moves:
            continue

        board.make_move(child.move)
        board.skip_move()
        child.score = __alpha_beta_iddfs_recursive(
            child, -infinity, infinity, eval_fn, depth-1
        )
        board.unmake_move()

        if child.score > best_score:
            best_score = child.score
            best_move = child.move
    
    board.make_move(best_move)
    duck_move = random.choice(board.generate_moves())
    board.make_move(duck_move)

    return (best_score, best_move, duck_move)
