""" Chessboard representation implementation
"""
from . import consts
from . import utils
from . import moves
from . import sides
from . import squares

from enum import Enum

class Board:
    def __init__(self):
        self.mailbox = [
            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R', 
            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.',
            '.', '.', '.', '.', '.', '.', '.', '.', 
            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
            'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
        ]

        self.white_pawns   = consts.INIT_WHITE_PAWNS
        self.white_knights = consts.INIT_WHITE_KNIGHTS
        self.white_bishops = consts.INIT_WHITE_BISHOPS
        self.white_rooks   = consts.INIT_WHITE_ROOKS
        self.white_queens  = consts.INIT_WHITE_QUEENS
        self.white_king    = consts.INIT_WHITE_KING
        self.white_pieces  = consts.INIT_WHITE_PIECES

        self.black_pawns   = consts.INIT_BLACK_PAWNS
        self.black_knights = consts.INIT_BLACK_KNIGHTS
        self.black_bishops = consts.INIT_BLACK_BISHOPS
        self.black_rooks   = consts.INIT_BLACK_ROOKS
        self.black_queens  = consts.INIT_BLACK_QUEENS
        self.black_king    = consts.INIT_BLACK_KING
        self.black_pieces  = consts.INIT_BLACK_PIECES

        self.duck = consts.INIT_DUCK

        self.turn = sides.Side.WHITE

    def occupied(self):
        return self.white_pieces | self.black_pieces | self.duck

    def empty(self):
        return utils.invert(self.occupied())

    def make_move(self, move: moves.Move):
        """ Applies the provided move to the board, updating all bitboards
            as required.
        """
        # Update mailbox
        self.mailbox[move.to_square] = self.mailbox[move.from_square]
        self.mailbox[move.from_square] = '.'

        # Update white pieces
        self.white_pawns   = move.apply(self.white_pawns)
        self.white_knights = move.apply(self.white_knights)
        self.white_bishops = move.apply(self.white_bishops)
        self.white_rooks   = move.apply(self.white_rooks)
        self.white_queens  = move.apply(self.white_queens)
        self.white_king    = move.apply(self.white_king)
        self.white_pieces  = move.apply(self.white_pieces)
        
        # Update black pieces
        self.black_pawns   = move.apply(self.black_pawns)
        self.black_knights = move.apply(self.black_knights)
        self.black_bishops = move.apply(self.black_bishops)
        self.black_rooks   = move.apply(self.black_rooks)
        self.black_queens  = move.apply(self.black_queens)
        self.black_king    = move.apply(self.black_king)
        self.black_pieces  = move.apply(self.black_pieces)

        # Update the duck
        self.duck = move.apply(self.duck)

    def unmake_move(self, move: moves.Move):
        """ Reverts the effect of the provided move on the board,
            updating all bitboards as required.
        """
        # Update mailbox
        self.mailbox[move.from_square] = self.mailbox[move.to_square]
        self.mailbox[move.to_square] = '.'

        # Update white pieces
        self.white_pawns   = move.revert(self.white_pawns)
        self.white_knights = move.revert(self.white_knights)
        self.white_bishops = move.revert(self.white_bishops)
        self.white_rooks   = move.revert(self.white_rooks)
        self.white_queens  = move.revert(self.white_queens)
        self.white_king    = move.revert(self.white_king)
        self.white_pieces  = move.revert(self.white_pieces)
        
        # Update black pieces
        self.black_pawns   = move.revert(self.black_pawns)
        self.black_knights = move.revert(self.black_knights)
        self.black_bishops = move.revert(self.black_bishops)
        self.black_rooks   = move.revert(self.black_rooks)
        self.black_queens  = move.revert(self.black_queens)
        self.black_king    = move.revert(self.black_king)
        self.black_pieces  = move.revert(self.black_pieces)

        # Update the duck
        self.duck = move.revert(self.duck)

    def generate_pawn_pushes(self):
        """ Returns an array of legal pawn pushes (i.e., non-captures), based 
            on whose turn it is (self.turn).
        """
        pawn_moves = []

        # Calculate relevant bitboards based on whose turn it is.
        if (self.turn == sides.Side.WHITE):
            # Bitboard with all pawns shifted up one space, where that space is not occupied.
            single_push_targets = (utils.north(self.white_pawns)    & self.empty())
            # Bitboard with all pawns shifted up another space, where neither is occupied and
            # the end square is on rank 4 (i.e., it was a valid double push).
            double_push_targets = (utils.north(single_push_targets) & self.empty()) & consts.RANK_4
            # Set move direction.
            direction = utils.Direction.NORTH
        elif (self.turn == sides.Side.BLACK):
            # As above, but flipped and for the black pawns.
            single_push_targets = (utils.south(self.black_pawns)    & self.empty())
            double_push_targets = (utils.south(single_push_targets) & self.empty()) & consts.RANK_5
            direction = utils.Direction.SOUTH

        for index in utils.get_squares(single_push_targets):
            pawn_moves.append(
                moves.Move(
                    from_index=index - direction,
                    to_index=index
                )
            )
        for index in utils.get_squares(double_push_targets):
            pawn_moves.append(
                moves.Move(
                    from_index=index - direction * 2,
                    to_index=index
                )
            )

        return pawn_moves

    def generate_pawn_captures(self):
        """ Generates attacking pawn moves (i.e., those that can capture an opposing
            piece.
        """
        pawn_captures = []

        # Set the appropriate pawn bitboard depending on whose turn it is.
        if (self.turn == sides.Side.WHITE):
            pawns = self.white_pawns
            enemies = self.black_pieces
        elif (self.turn == sides.Side.BLACK):
            pawns = self.black_pawns
            enemies = self.white_pieces

        # Loop through all of this side's pawns.
        for pawn in utils.get_squares(pawns):
            # Get the capture template for this pawn.
            template = moves.PAWN_CAPTURE_TEMPLATES[self.turn][pawn]
            # Find capture targets (if any).
            targets = template & enemies
            for target in utils.get_squares(targets):
                pawn_captures.append(
                    moves.Move(
                        from_index=pawn,
                        to_index=target
                    )
                )
        return pawn_captures

    def generate_knight_moves(self):
        """ Generates knight moves for the current side.
        """
        knight_moves = []

        # Set the appropriate knight bitboard depending on whose turn it is.
        if (self.turn == sides.Side.WHITE):
            knights = self.white_knights
            allies = self.white_pieces
        elif (self.turn == sides.Side.BLACK):
            knights = self.black_knights
            allies = self.white_pieces
        
        # Loop through all of this side's knights.
        for knight in utils.get_squares(knights):
            # Get the move template for this knight.
            template = moves.KNIGHT_TEMPLATES[knight]
            # Find legal targets (if any).
            targets = template & utils.invert(allies)
            for target in utils.get_squares(targets):
                knight_moves.append(
                    moves.Move(
                        from_index=knight,
                        to_index=target
                    )
                )
        return knight_moves

    def generate_bishop_moves(self):
        """ Generates bishop moves for the current side.
        """
        bishop_moves = []

        # Set the appropriate bishop bitboard depending on whose turn it is.
        if (self.turn == sides.Side.WHITE):
            bishops = self.white_bishops
            allies = self.white_pieces
        elif (self.turn == sides.Side.BLACK):
            bishops = self.black_bishops
            allies = self.black_pieces

        # Loop through all of this side's bishops.
        for bishop in utils.get_squares(bishops):
            # Generate a move template along the diagonal (a1-h8 axis).
            template_diag = utils.hyperbola_quintessence(
                self.occupied(), 
                utils.get_diagonal(bishop),
                squares.masks[bishop]
            )
            # Generate a move template along the antidiagonal (a8-h1 axis).
            template_anti = utils.hyperbola_quintessence(
                self.occupied(),
                utils.get_antidiagonal(bishop),
                squares.masks[bishop]
            )
            # Combine the above to get the full move template.
            template = template_diag | template_anti
            # Remove allied squares from the template.
            targets = template & utils.invert(allies)

            # Loop through the legal target squares and add the relevant move.
            for target in utils.get_squares(targets):
                bishop_moves.append(
                    moves.Move(
                        from_index=bishop,
                        to_index=target
                    )
                )
        
        return bishop_moves

    def generate_rook_moves(self):
        """ Generates rook moves for the current side.
        """
        rook_moves = []

        # Set the appropriate rook bitboard depending on whose turn it is.
        if (self.turn == sides.Side.WHITE):
            rooks = self.white_rooks
            allies = self.white_pieces
        elif (self.turn == sides.Side.BLACK):
            rooks = self.black_rooks
            allies = self.black_pieces
        
        # Loop through all of this side's rooks.
        for rook in utils.get_squares(rooks):
            # Generate a move template along the rank
            template_rank = utils.hyperbola_quintessence(
                self.occupied(),
                utils.get_rank(rook),
                squares.masks[rook]
            )
            # Generate a move template along the file
            template_file = utils.hyperbola_quintessence(
                self.occupied(),
                utils.get_file(rook),
                squares.masks[rook]
            )
            # Combine the above to get the full move template.
            template = template_rank | template_file
            targets = template & utils.invert(allies)

            for target in utils.get_squares(targets):
                rook_moves.append(
                    moves.Move(
                        from_index=rook,
                        to_index=target
                    )
                )

    def get_legal_moves(self):
        pass

    def __str__(self):
        result = ''
        for s in range(len(self.mailbox), 0, -8):
            result += ''.join(self.mailbox[s-8:s]) + '\n'
        return result.strip('\n')
