""" Mailbox unit tests """
import unittest
from chess.board import Board
from chess.moves import Move, MoveType
from chess.pieces import Piece, PieceType
from chess.sides import Side
from chess.consts import *
from chess.squares import *

class TestMailbox(unittest.TestCase):
    def test_quiet_move(self):
        board = Board()
        move = Move.from_string("b1c3", MoveType.QUIET)
        
        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_KNIGHT)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_KNIGHT)
        self.assertEqual(board.mailbox[move.to_index], Piece.EMPTY)

    def test_double_pawn_move(self):
        board = Board()
        move = Move.from_string("e2e4", MoveType.DOUBLE_PAWN)
        
        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_PAWN)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_PAWN)
        self.assertEqual(board.mailbox[move.to_index], Piece.EMPTY)

    def test_capture_move(self):
        board = Board.from_fen_string("1kr5/ppp5/4p3/8/3N4/8/PPP5/1KR5 w - - 0 1")
        move = Move.from_string("d4e6", MoveType.CAPTURE)

        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_KNIGHT)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_KNIGHT)
        self.assertEqual(board.mailbox[move.to_index], Piece.B_PAWN)

    def test_promotion_move(self):
        board = Board.from_fen_string("8/2kPK3/8/8/8/8/8/8 w - - 0 1")
        move = Move.from_string("d7d8=Q", MoveType.PROMOTION)

        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_QUEEN)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_PAWN)
        self.assertEqual(board.mailbox[move.to_index], Piece.EMPTY)

    def test_en_passant_move(self):
        board = Board.from_fen_string("r1bqkb1r/ppp1pppp/2n2n2/3pP3/8/5N2/PPPP1PPP/RNBQKB1R w KQkq d6 0 1")
        move = Move.from_string("e5d6", MoveType.EN_PASSANT)

        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_PAWN)
        self.assertEqual(board.mailbox[move.to_index - 8], Piece.EMPTY)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_PAWN)
        self.assertEqual(board.mailbox[move.to_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index - 8], Piece.B_PAWN)
        
    def test_capture_promotion_move(self):
        board = Board.from_fen_string("7r/1k4P1/8/8/8/8/6R1/8 w - - 0 1")
        move = Move.from_string("g7h8=Q", MoveType.CAPTURE_PROMOTION)

        board.make_move(move)

        self.assertEqual(board.mailbox[move.from_index], Piece.EMPTY)
        self.assertEqual(board.mailbox[move.to_index], Piece.W_QUEEN)

        board.unmake_move()

        self.assertEqual(board.mailbox[move.from_index], Piece.W_PAWN)
        self.assertEqual(board.mailbox[move.to_index], Piece.B_ROOK)

    def test_castle_kingside_move(self):
        board = Board.from_fen_string("r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
        move = Move.from_string("O-O", MoveType.CASTLE_KINGSIDE)

        board.make_move(move)

        self.assertEqual(board.mailbox[squares.e1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.f1], Piece.W_ROOK)
        self.assertEqual(board.mailbox[squares.g1], Piece.W_KING)
        self.assertEqual(board.mailbox[squares.h1], Piece.EMPTY)

        board.unmake_move()

        self.assertEqual(board.mailbox[squares.e1], Piece.W_KING)
        self.assertEqual(board.mailbox[squares.f1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.g1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.h1], Piece.W_ROOK)

    def test_castle_queenside_move(self):
        board = Board.from_fen_string("rnbqkb1r/pp2pppp/2p2n2/3p4/3P1B2/2N5/PPPQPPPP/R3KBNR w KQkq - 0 1")
        move = Move.from_string("O-O-O", MoveType.CASTLE_QUEENSIDE)

        board.make_move(move)

        self.assertEqual(board.mailbox[squares.a1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.b1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.c1], Piece.W_KING)
        self.assertEqual(board.mailbox[squares.d1], Piece.W_ROOK)
        self.assertEqual(board.mailbox[squares.e1], Piece.EMPTY)

        board.unmake_move()

        self.assertEqual(board.mailbox[squares.a1], Piece.W_ROOK)
        self.assertEqual(board.mailbox[squares.b1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.c1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.d1], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.e1], Piece.W_KING)

    def test_duck_move(self):
        board = Board.from_fen_string("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w@ KQkq - 0 1")
        white_move = Move.from_string("@c4", MoveType.DUCK)
        black_move = Move.from_string("@c4f4", MoveType.DUCK)

        board.make_move(white_move)
        board.skip_move()
        board.make_move(black_move)

        self.assertEqual(board.mailbox[squares.c4], Piece.EMPTY)
        self.assertEqual(board.mailbox[squares.f4], Piece.DUCK)

        board.unmake_move()

        self.assertEqual(board.mailbox[squares.c4], Piece.DUCK)
        self.assertEqual(board.mailbox[squares.f4], Piece.EMPTY)
