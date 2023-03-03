""" Move generation unit tests """
import unittest
from chess.board import Board
from chess.moves import Move, MoveType

class TestMoveGeneration(unittest.TestCase):
    def test_starting_position(self):
        board = Board()
        moves = board.generate_moves()        
        self.assertEqual(len(moves), 20)

    def test_pawn_moves(self):
        board = Board.from_fen_string("1k6/8/8/5pp1/4pPP1/1PpP4/P1P1P3/1K6 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type != MoveType.KING}

        expected = {
            Move.from_string("a2a3", MoveType.PAWN_SINGLE),
            Move.from_string("a2a4", MoveType.PAWN_DOUBLE),
            Move.from_string("b3b4", MoveType.PAWN_SINGLE),
            Move.from_string("d3e4", MoveType.PAWN_CAPTURE),
            Move.from_string("d3d4", MoveType.PAWN_SINGLE),
            Move.from_string("e2e3", MoveType.PAWN_SINGLE),
            Move.from_string("f4g5", MoveType.PAWN_CAPTURE),
            Move.from_string("g4f5", MoveType.PAWN_CAPTURE),
        }

        self.assertSetEqual(moves, expected)

    def test_pawn_promotions(self):
        board = Board.from_fen_string("r3k3/1P6/8/8/8/8/8/4K3 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type != MoveType.KING}
        expected = {
            # Pushes
            Move.from_string("b7b8=N", MoveType.PAWN_PROMOTION),
            Move.from_string("b7b8=B", MoveType.PAWN_PROMOTION),
            Move.from_string("b7b8=R", MoveType.PAWN_PROMOTION),
            Move.from_string("b7b8=Q", MoveType.PAWN_PROMOTION),
            # Captures
            Move.from_string("b7a8=N", MoveType.PAWN_CAPTURE_PROMOTION),
            Move.from_string("b7a8=B", MoveType.PAWN_CAPTURE_PROMOTION),
            Move.from_string("b7a8=R", MoveType.PAWN_CAPTURE_PROMOTION),
            Move.from_string("b7a8=Q", MoveType.PAWN_CAPTURE_PROMOTION),
        }

        self.assertSetEqual(moves, expected)

    def test_knight_moves(self):
        board = Board.from_fen_string("4k3/8/3p2p1/p4P2/2N4N/P7/3P4/4K3 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type == MoveType.KNIGHT}

        expected = {
            # c4 knight
            Move.from_string("c4a5", MoveType.KNIGHT),
            Move.from_string("c4b6", MoveType.KNIGHT),
            Move.from_string("c4d6", MoveType.KNIGHT),
            Move.from_string("c4e5", MoveType.KNIGHT),
            Move.from_string("c4e3", MoveType.KNIGHT),
            Move.from_string("c4b2", MoveType.KNIGHT),
            # h4 knight
            Move.from_string("h4g6", MoveType.KNIGHT),
            Move.from_string("h4f3", MoveType.KNIGHT),
            Move.from_string("h4g2", MoveType.KNIGHT),
        }

        self.assertSetEqual(moves, expected)

    def test_bishop_moves(self):
        board = Board.from_fen_string("1k6/1P6/6p1/3p3B/4B3/2PP4/6p1/B5K1 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type == MoveType.BISHOP}

        expected = {
            # a1 bishop
            Move.from_string("a1b2", MoveType.BISHOP),
            # e4 bishop
            Move.from_string("e4d5", MoveType.BISHOP),
            Move.from_string("e4f3", MoveType.BISHOP),
            Move.from_string("e4g2", MoveType.BISHOP),
            Move.from_string("e4f5", MoveType.BISHOP),
            Move.from_string("e4g6", MoveType.BISHOP),
            # h5 bishop
            Move.from_string("h5g6", MoveType.BISHOP),
            Move.from_string("h5g4", MoveType.BISHOP),
            Move.from_string("h5f3", MoveType.BISHOP),
            Move.from_string("h5e2", MoveType.BISHOP),
            Move.from_string("h5d1", MoveType.BISHOP),
        }

        self.assertSetEqual(moves, expected)

    def test_rook_moves(self):
        board = Board.from_fen_string("8/6p1/P7/5bRP/3R4/3p4/R7/8 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type == MoveType.ROOK}

        expected = {
            # a2 rook
            Move.from_string("a2a1", MoveType.ROOK),
            Move.from_string("a2a3", MoveType.ROOK),
            Move.from_string("a2a4", MoveType.ROOK),
            Move.from_string("a2a5", MoveType.ROOK),
            Move.from_string("a2b2", MoveType.ROOK),
            Move.from_string("a2c2", MoveType.ROOK),
            Move.from_string("a2d2", MoveType.ROOK),
            Move.from_string("a2e2", MoveType.ROOK),
            Move.from_string("a2f2", MoveType.ROOK),
            Move.from_string("a2g2", MoveType.ROOK),
            Move.from_string("a2h2", MoveType.ROOK),
            # d4 rook
            Move.from_string("d4c4", MoveType.ROOK),
            Move.from_string("d4b4", MoveType.ROOK),
            Move.from_string("d4a4", MoveType.ROOK),
            Move.from_string("d4d3", MoveType.ROOK),
            Move.from_string("d4d5", MoveType.ROOK),
            Move.from_string("d4d6", MoveType.ROOK),
            Move.from_string("d4d7", MoveType.ROOK),
            Move.from_string("d4d8", MoveType.ROOK),
            Move.from_string("d4e4", MoveType.ROOK),
            Move.from_string("d4f4", MoveType.ROOK),
            Move.from_string("d4g4", MoveType.ROOK),
            Move.from_string("d4h4", MoveType.ROOK),
            # g5 rook
            Move.from_string("g5f5", MoveType.ROOK),
            Move.from_string("g5g6", MoveType.ROOK),
            Move.from_string("g5g7", MoveType.ROOK),
            Move.from_string("g5g4", MoveType.ROOK),
            Move.from_string("g5g3", MoveType.ROOK),
            Move.from_string("g5g2", MoveType.ROOK),
            Move.from_string("g5g1", MoveType.ROOK),
        }

        self.assertSetEqual(moves, expected)

    def test_queen_moves(self):
        board = Board.from_fen_string("8/4p1p1/1P2Q3/3P4/3Q4/8/1n2r3/8 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type == MoveType.QUEEN}

        expected = {
            # d4 queen
            Move.from_string("d4c4", MoveType.QUEEN), 
            Move.from_string("d4b4", MoveType.QUEEN),
            Move.from_string("d4a4", MoveType.QUEEN), 
            Move.from_string("d4c5", MoveType.QUEEN),
            Move.from_string("d4e5", MoveType.QUEEN), 
            Move.from_string("d4f6", MoveType.QUEEN),
            Move.from_string("d4g7", MoveType.QUEEN), 
            Move.from_string("d4e4", MoveType.QUEEN),
            Move.from_string("d4f4", MoveType.QUEEN), 
            Move.from_string("d4g4", MoveType.QUEEN),
            Move.from_string("d4h4", MoveType.QUEEN), 
            Move.from_string("d4e3", MoveType.QUEEN),
            Move.from_string("d4f2", MoveType.QUEEN), 
            Move.from_string("d4g1", MoveType.QUEEN),
            Move.from_string("d4d3", MoveType.QUEEN), 
            Move.from_string("d4d2", MoveType.QUEEN),
            Move.from_string("d4d1", MoveType.QUEEN), 
            Move.from_string("d4c3", MoveType.QUEEN),
            Move.from_string("d4b2", MoveType.QUEEN),
            # e6 queen
            Move.from_string("e6d6", MoveType.QUEEN), 
            Move.from_string("e6c6", MoveType.QUEEN),
            Move.from_string("e6e7", MoveType.QUEEN), 
            Move.from_string("e6f7", MoveType.QUEEN),
            Move.from_string("e6g8", MoveType.QUEEN), 
            Move.from_string("e6f6", MoveType.QUEEN),
            Move.from_string("e6g6", MoveType.QUEEN), 
            Move.from_string("e6h6", MoveType.QUEEN),
            Move.from_string("e6f5", MoveType.QUEEN), 
            Move.from_string("e6g4", MoveType.QUEEN),
            Move.from_string("e6h3", MoveType.QUEEN), 
            Move.from_string("e6e5", MoveType.QUEEN),
            Move.from_string("e6e4", MoveType.QUEEN), 
            Move.from_string("e6e3", MoveType.QUEEN),
            Move.from_string("e6e2", MoveType.QUEEN), 
            Move.from_string("e6d7", MoveType.QUEEN), 
            Move.from_string("e6c8", MoveType.QUEEN), 
        }

        self.assertSetEqual(moves, expected)

    def test_king_moves(self):
        board = Board.from_fen_string("8/8/8/8/1p1r4/1PK5/3N4/8 w - - 0 1")
        moves = board.get_legal_moves()
        moves = {m for m in moves if m.move_type == MoveType.KING}

        expected = {
            Move.from_string("c3b4", MoveType.KING),
            Move.from_string("c3c4", MoveType.KING),
            Move.from_string("c3d4", MoveType.KING),
            Move.from_string("c3d3", MoveType.KING),
            Move.from_string("c3c2", MoveType.KING),
            Move.from_string("c3b2", MoveType.KING),
        }

        self.assertSetEqual(moves, expected)

    def test_castling(self):
        # Base case, no obstruction, all castling rights
        board = Board.from_fen_string("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = {
            Move.from_string("O-O"),
            Move.from_string("O-O-O")
        }

        self.assertSetEqual(moves, expected)

        # As above, no castling rights
        board = Board.from_fen_string("4k3/8/8/8/8/8/8/R3K2R w - - 0 1")
        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = set()

        self.assertSetEqual(moves, expected)
        
        # Case with blockers (allied and enemy)
        board = Board.from_fen_string("4k3/8/8/8/8/8/8/R1n1K1NR w KQ - 0 1")
        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = set()

        self.assertSetEqual(moves, expected)

    def test_castling_rights(self):
        # Test rook moves remove castle rights
        board = Board.from_fen_string("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
        # Move queenside rook, should then prevent queenside castling
        board.make_move(Move.from_string("a1b1"))
        # Skip to the next white move
        board.skip_move()
        board.skip_move()
        board.skip_move()

        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = {
            Move.from_string("O-O")
        }

        self.assertSetEqual(moves, expected)

        # Test king moves remove castle rights
        board = Board.from_fen_string("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
        # Move king, should prevent all castling
        board.make_move(Move.from_string("e1e2"))
        # Skip to the next white move
        board.skip_move()
        board.skip_move()
        board.skip_move()

        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = set()

        self.assertSetEqual(moves, expected)

        # Test rook capture, should remove castle rights on that side
        board = Board.from_fen_string("4k3/8/8/8/8/8/2n5/R3K2R b KQ - 0 1")
        # Capture a rook, should prevent queenside castling
        board.make_move(Move.from_string("c2a1"))
        # Skip to white's move
        board.skip_move()

        moves = board.get_legal_moves()
        moves = {
            m for m in moves
            if m.move_type in (
                MoveType.CASTLE_KINGSIDE, MoveType.CASTLE_QUEENSIDE
            )
        }

        expected = {
            Move.from_string("O-O")
        }

        self.assertSetEqual(moves, expected)
