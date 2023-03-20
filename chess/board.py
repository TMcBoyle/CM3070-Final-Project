""" Chessboard representation implementation
"""

from .consts import *
from .moves import *
from .pieces import Piece, PieceType, PIECE_MASK, SIDE_MASK
from .sides import Side, next_turn, opposing_side
from .zobrist import zbr_hash, zbr_update

from . import squares

from dataclasses import dataclass
from enum import IntEnum

class GameState(IntEnum):
    ONGOING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3

@dataclass
class PositionProperties:
    """ Dataclass for storing the properties of a position.
    """
    game_state: GameState = None
    turn: Side = None
    duck: int = None
    castle_rights: int = None
    en_passant: int = None
    halfmove_clock: int = None
    fullmove_count: int = None
    capture: PieceType = None
    move: Move = None
    zbr: int = None

@dataclass
class PositionBoards:
    """ Dataclass for storing the bitboards of a position.
    """
    # Player pieces. Defaults to the starting position - this is
    # handled in __post_init__.
    pieces: dict[Side, PieceType] = None
    # Aggregate bitboards, to be updated incrementally.
    duck: int = INIT_DUCK
    white: int = INIT_WHITE_PIECES
    black: int = INIT_BLACK_PIECES
    occupied: int = INIT_ALL_PIECES

    def __post_init__(self):
        if not self.pieces:
            self.pieces = {
                Side.WHITE: {
                    PieceType.PAWN: INIT_WHITE_PAWNS,
                    PieceType.KNIGHT: INIT_WHITE_KNIGHTS,
                    PieceType.BISHOP: INIT_WHITE_BISHOPS,
                    PieceType.ROOK: INIT_WHITE_ROOKS,
                    PieceType.QUEEN: INIT_WHITE_QUEENS,
                    PieceType.KING: INIT_WHITE_KING
                },
                Side.BLACK: {
                    PieceType.PAWN: INIT_BLACK_PAWNS,
                    PieceType.KNIGHT: INIT_BLACK_KNIGHTS,
                    PieceType.BISHOP: INIT_BLACK_BISHOPS,
                    PieceType.ROOK: INIT_BLACK_ROOKS,
                    PieceType.QUEEN: INIT_BLACK_QUEENS,
                    PieceType.KING: INIT_BLACK_KING
                }
            }

class Board:
    """ Duck chess board representation.
    """
    def __init__(self):
        self.boards = PositionBoards()

        self.turn = Side.WHITE
        self.castle_rights = INIT_CASTLE_RIGHTS
        self.en_passant = EMPTY
        self.halfmove_clock = 0
        self.fullmove_count = 0
        self.game_state = GameState.ONGOING

        self.mailbox = [
            Piece.W_ROOK, Piece.W_KNIGHT, Piece.W_BISHOP, Piece.W_QUEEN, Piece.W_KING, Piece.W_BISHOP, Piece.W_KNIGHT, Piece.W_ROOK,
            Piece.W_PAWN, Piece.W_PAWN,   Piece.W_PAWN,   Piece.W_PAWN,  Piece.W_PAWN, Piece.W_PAWN,   Piece.W_PAWN,   Piece.W_PAWN,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,   Piece.EMPTY,  Piece.EMPTY,    Piece.EMPTY,    Piece.EMPTY,
            Piece.B_PAWN, Piece.B_PAWN,   Piece.B_PAWN,   Piece.B_PAWN,  Piece.B_PAWN, Piece.B_PAWN,   Piece.B_PAWN,   Piece.B_PAWN,
            Piece.B_ROOK, Piece.B_KNIGHT, Piece.B_BISHOP, Piece.B_QUEEN, Piece.B_KING, Piece.B_BISHOP, Piece.B_KNIGHT, Piece.B_ROOK,
        ]

        # Initialise Zobrist Hash value.
        self.zbr = zbr_hash(self)

        # Initialise history
        self.history = [
            PositionProperties(
                game_state=self.game_state,
                turn=self.turn,
                duck=self.boards.duck,
                castle_rights=self.castle_rights,
                en_passant=self.en_passant,
                halfmove_clock=self.halfmove_clock,
                fullmove_count=self.fullmove_count,
                capture=Piece.EMPTY,
                move=None,
                zbr=self.zbr
            )
        ]

    def to_fen_string(self) -> str:
        """ Builds a FEN-style string from the current board state """
        result = ""
        blank_count = 0
        mailbox_reshaped = [self.mailbox[n-8:n] for n in range(64, 0, -8)]
        
        # Pieces
        for rank in mailbox_reshaped:
            for piece in rank:
                if piece == Piece.EMPTY:
                    blank_count += 1
                else:
                    if blank_count > 0:
                        result += str(blank_count)
                        blank_count = 0
                    result += pieces.symbols[piece]
        
            if blank_count > 0:
                result += str(blank_count)
                blank_count = 0
            result += "/"
        result = result.strip("/")
        result += " "

        # Turn
        if self.turn == Side.WHITE:
            result += "w"
        elif self.turn == Side.WHITE_DUCK:
            result += "w@"
        elif self.turn == Side.BLACK:
            result += "b"
        elif self.turn == Side.BLACK_DUCK:
            result += "b@"
        result += " "

        # Castling Rights
        if self.castle_rights == EMPTY:
            result += "-"
        else:
            if self.castle_rights & squares.masks[squares.h1]:
                result += "K"
            if self.castle_rights & squares.masks[squares.a1]:
                result += "Q"
            if self.castle_rights & squares.masks[squares.a8]:
                result += "k"
            if self.castle_rights & squares.masks[squares.a8]:
                result += "q"
        result += " "

        # En passant
        if self.en_passant == EMPTY:
            result += "-"
        else:
            ep_index = utils.ls1b_index(self.en_passant)
            result += squares.labels[ep_index]

        # Move counts
        result += f" {self.halfmove_clock} {self.fullmove_count}"

        return result

    def from_fen_string(string: str) -> "Board":
        """ Creates a board from a FEN-style string """
        fields = string.split(" ")
        ranks = fields[0]
        turn = fields[1]
        castle_rights = fields[2]
        en_passant = fields[3]
        halfmove_clock = int(fields[4])
        fullmove_count = int(fields[5])

        board = Board()
        board.mailbox = [Piece.EMPTY] * 64
        for side in board.boards.pieces:
            for piece in board.boards.pieces[side]:
                board.boards.pieces[side][piece] = EMPTY

        idx = 0
        for rank in reversed(ranks.split("/")):
            for square in rank:
                # Empty cells
                if square.isnumeric():
                    idx += int(square)
                    continue
                # Duck
                elif square == pieces.symbols[Piece.DUCK]:
                    board.duck = squares.masks[idx]
                    board.mailbox[idx] = Piece.DUCK
                # Pieces
                else:
                    piece = pieces.symbol_lookup[square]
                    board.boards.pieces[piece & SIDE_MASK][piece & PIECE_MASK] \
                        |= squares.masks[idx]
                    board.mailbox[idx] = piece
                idx += 1
        
        # Set turn
        if turn == "w":
            board.turn = Side.WHITE
        elif turn == "w@":
            board.turn = Side.WHITE_DUCK
        elif turn == "b":
            board.turn = Side.BLACK
        elif turn == "b@":
            board.turn = Side.BLACK_DUCK

        # Set castling rights
        board.castle_rights = consts.EMPTY
        if "Q" in castle_rights:
            board.castle_rights |= squares.masks[squares.a1]
        if "K" in castle_rights:
            board.castle_rights |= squares.masks[squares.h1]
        if "q" in castle_rights:
            board.castle_rights |= squares.masks[squares.a8]
        if "k" in castle_rights:
            board.castle_rights |= squares.masks[squares.h8]

        # Set en passant
        if en_passant != "-":
            board.en_passant = squares.masks[squares.labels.index(en_passant)]

        # Set move counts
        board.halfmove_clock = halfmove_clock
        board.fullmove_count = fullmove_count

        # Set aggregate bitboards
        board.boards.white = EMPTY
        for bitboard in board.boards.pieces[Side.WHITE].values():
            board.boards.white |= bitboard
        board.boards.black = EMPTY
        for bitboard in board.boards.pieces[Side.BLACK].values():
            board.boards.black |= bitboard

        board.boards.occupied = \
            board.boards.white | board.boards.black | board.boards.duck
        
        board.zbr = zbr_hash(board)

        return board

    def update_game_state(self):
        if self.boards.pieces[Side.WHITE][PieceType.KING] == consts.EMPTY:
            self.game_state = GameState.BLACK_WINS
        elif self.boards.pieces[Side.BLACK][PieceType.KING] == consts.EMPTY:
            self.game_state = GameState.WHITE_WINS
        elif self.halfmove_clock >= 50 or len(self.generate_moves()) == 0:
            self.game_state = GameState.STALEMATE

    def skip_move(self):
        """ Advanced the turn order without making a move. En passant state is preserved,
            move counts aren't updated.
        """
        previous = self.turn
        self.turn = sides.next_turn(self.turn)
        self.zbr = zbr_update(self.zbr, (
            PositionProperties(turn=previous, castle_rights=self.castle_rights, en_passant=self.en_passant),
            PositionProperties(turn=self.turn, castle_rights=self.castle_rights, en_passant=self.en_passant)
        ))

    def generate_moves(self, pseudo: bool=False):
        """ Returns a list of valid moves in the position. If
            pseudo is true, the duck is ignored and a pseudolegal move
            list is generated instead.
        """
        occupation = self.boards.occupied ^ (self.boards.duck if pseudo else EMPTY)
        duck = self.boards.duck if not pseudo else EMPTY

        # Return just the duck moves if it's a duck turn.
        if self.turn in (Side.WHITE_DUCK, Side.BLACK_DUCK):
            return duck_moves(self.boards.duck, occupation)
        
        # Set bitboards to use based on the current turn.
        pieces = self.boards.pieces[self.turn]
        allies = self.boards.white if self.turn == Side.WHITE else self.boards.black
        enemies = self.boards.white if self.turn == Side.BLACK else self.boards.black

        # Generate the moves.
        moves = []
        moves += pawn_captures(pieces[PieceType.PAWN],   enemies,    self.turn)
        moves += pawn_pushes  (pieces[PieceType.PAWN],   occupation, self.turn)
        moves += knight_moves (pieces[PieceType.KNIGHT], occupation, allies | duck)
        moves += bishop_moves (pieces[PieceType.BISHOP], occupation, allies | duck)
        moves += rook_moves   (pieces[PieceType.ROOK],   occupation, allies | duck)
        moves += queen_moves  (pieces[PieceType.QUEEN],  occupation, allies | duck)
        moves += king_moves   (pieces[PieceType.KING],   occupation, allies | duck)
        moves += castling     (occupation, self.castle_rights, self.turn)

        return moves

    def __move_piece(self, from_index: int, to_index: int, piece: PieceType):
        """ Helper function to move a piece and update the mailbox accordingly.
        """
        from_mask = squares.masks[from_index]
        to_mask = squares.masks[to_index]
        # Move the piece
        self.boards.pieces[self.turn][piece] ^= from_mask | to_mask
        if self.turn == sides.Side.WHITE:
            self.boards.white ^= from_mask | to_mask
        elif self.turn == sides.Side.BLACK:
            self.boards.black ^= from_mask | to_mask
        # Update the mailbox
        self.mailbox[from_index] = Piece.EMPTY
        self.mailbox[to_index] = piece | self.turn

    def __move_and_change_piece(self, from_index: int, to_index: int, from_piece: PieceType, to_piece: PieceType):
        """ Helper function to move and change the type of a piece (i.e., for promotions).
        """
        from_mask = squares.masks[from_index]
        to_mask = squares.masks[to_index]
        # Remove the old piece, add the new piece
        self.boards.pieces[self.turn][from_piece] &= utils.invert(from_mask)
        self.boards.pieces[self.turn][to_piece] |= to_mask
        if self.turn == sides.Side.WHITE:
            self.boards.white ^= from_mask | to_mask
        elif self.turn == sides.Side.BLACK:
            self.boards.black ^= from_mask | to_mask
        # Update the mailbox
        self.mailbox[from_index] = Piece.EMPTY
        self.mailbox[to_index] = to_piece | self.turn

    def __add_piece(self, add_index: int, side: Side, piece: Piece):
        """ Helper function to add a piece to the board (i.e., for reversing
            captures).
        """
        add_mask = squares.masks[add_index]
        self.boards.pieces[side][piece & PIECE_MASK] |= add_mask
        if side == sides.Side.WHITE:
            self.boards.white |= add_mask
        elif side == sides.Side.BLACK:
            self.boards.black |= add_mask
        self.mailbox[add_index] = piece | side

    def __remove_piece(self, capture_index: int) -> Piece:
        """ Helper function to remove a piece from the board (i.e., for captures).
            Returns the type of piece captured.
        """
        # Identify the captured piece and store in properties
        capture_mask = squares.masks[capture_index]
        captured_piece = self.mailbox[capture_index]
        captured_type = captured_piece & PIECE_MASK
        # Remove the captured piece
        self.boards.pieces[opposing_side(self.turn)][captured_type] &= utils.invert(capture_mask)
        if self.turn == sides.Side.WHITE:
            self.boards.black &= utils.invert(capture_mask)
        elif self.turn == sides.Side.BLACK:
            self.boards.white &= utils.invert(capture_mask)
        self.mailbox[capture_index] = Piece.EMPTY
        return captured_piece

    def __update_castling_rights(self, move: Move):
        """ Helper function to update castling rights based on a move.
        """
        from_mask = squares.masks[move.from_index]
        to_mask = squares.masks[move.to_index]

        self.castle_rights &= utils.invert(from_mask)
        self.castle_rights &= utils.invert(to_mask)

        if move.piece == PieceType.KING:
                if self.turn == Side.WHITE:
                    self.castle_rights &= utils.invert(consts.RANK_1)
                elif self.turn == Side.BLACK:
                    self.castle_rights &= utils.invert(consts.RANK_8)

    def make_move(self, move: Move):
        """ Applies the provided move to the board.
            IMPORTANT: This method assumes a legal move is passed.
        """
        # Build new position properties object
        properties = PositionProperties(
            game_state=self.game_state,
            turn=self.turn,
            duck=self.boards.duck,
            castle_rights=self.castle_rights,
            en_passant=self.en_passant,
            halfmove_clock=self.halfmove_clock,
            fullmove_count=self.fullmove_count,
            capture=Piece.EMPTY,
            move=move,
            zbr=self.zbr
        )

        # Set piece type if not already known (i.e., for manual moves)
        if not move.piece:
            move.piece = self.mailbox[move.from_index] & PIECE_MASK

        # Get from/to masks
        if move.from_index is not None:
            from_mask = squares.masks[move.from_index]
        if move.to_index is not None:
            to_mask = squares.masks[move.to_index]

        # Quiet moves
        if move.move_type == MoveType.QUIET:
            # Move the piece
            self.__move_piece(move.from_index, move.to_index, move.piece)
            # Unset en passant
            self.en_passant = EMPTY
            # Update castling rights if needed
            self.__update_castling_rights(move)
        # Double pawn moves
        elif move.move_type == MoveType.DOUBLE_PAWN:
            # Move the piece
            self.__move_piece(move.from_index, move.to_index, move.piece)
            # Set en passant square
            self.en_passant = \
                utils.south(to_mask) if self.turn == Side.WHITE \
                else utils.north(to_mask)
        # Captures
        elif move.move_type == MoveType.CAPTURE:
            # Remove the captured piece and store in properties
            properties.capture = self.__remove_piece(move.to_index)
            # Move the piece
            self.__move_piece(move.from_index, move.to_index, move.piece)
            # Unset en passant
            self.en_passant = EMPTY
            # Update castling rights if needed
            self.__update_castling_rights(move)
        # Promotions
        elif move.move_type == MoveType.PROMOTION:
            self.__move_and_change_piece(
                move.from_index,
                move.to_index,
                move.piece,
                move.promotion
            )
            # Unset en passant
            self.en_passant = EMPTY
        # En Passant
        elif move.move_type == MoveType.EN_PASSANT:
            # Remove the captured piece and store in properties
            capture_mask = \
                utils.south(to_mask) if self.turn == Side.WHITE \
                else utils.north(to_mask)
            capture_index = utils.ls1b_index(capture_mask)
            properties.capture = self.__remove_piece(capture_index)
            # Move the piece
            self.__move_piece(move.from_index, move.to_index, move.piece)
            # Unset en passant
            self.en_passant = EMPTY
        # Capture promotions
        elif move.move_type == MoveType.CAPTURE_PROMOTION:
            # Remove the captured piece and store in properties
            properties.capture = self.__remove_piece(move.to_index)
            # Perform the promotion
            self.__move_and_change_piece(
                move.from_index,
                move.to_index,
                move.piece,
                move.promotion
            )
            # Unset en passant
            self.en_passant = EMPTY
            # Update castling rights if needed
            self.__update_castling_rights(move)
        # Kingside Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            if self.turn == Side.WHITE:
                self.__move_piece(squares.e1, squares.g1, PieceType.KING)
                self.__move_piece(squares.h1, squares.f1, PieceType.ROOK)
                self.castle_rights &= utils.invert(consts.RANK_1)
            elif self.turn == Side.BLACK:
                self.__move_piece(squares.e8, squares.g8, PieceType.KING)
                self.__move_piece(squares.h8, squares.f8, PieceType.ROOK)
                self.castle_rights &= utils.invert(consts.RANK_8)
            # Unset en passant
            self.en_passant = EMPTY
        # Queenside Castling
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            if self.turn == Side.WHITE:
                self.__move_piece(squares.e1, squares.c1, PieceType.KING)
                self.__move_piece(squares.a1, squares.d1, PieceType.ROOK)
                self.castle_rights &= utils.invert(consts.RANK_1)
            elif self.turn == Side.BLACK:
                self.__move_piece(squares.e8, squares.c8, PieceType.KING)
                self.__move_piece(squares.a8, squares.d8, PieceType.ROOK)
                self.castle_rights &= utils.invert(consts.RANK_8)
            # Unset en passant
            self.en_passant = EMPTY
        # Duck moves
        elif move.move_type == MoveType.DUCK:
            self.boards.duck = to_mask

        # Update Zobrist hash and history
        self.zbr = zbr_update(
            self.zbr,
            (self.history[-1], properties),
            self.turn,
            move,
            properties.capture
        )
        self.history.append(properties)

        # Update move counts, occupied board, turn and game state
        if move.piece == PieceType.PAWN or (move.move_type & MoveType.CAPTURE):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        if self.turn == Side.BLACK_DUCK:
            self.fullmove_count += 1
        self.boards.occupied = self.boards.white | self.boards.black | self.boards.duck
        self.turn = next_turn(self.turn)
        self.update_game_state()

    def unmake_move(self):
        """ Reverts the last played move and restores position properties such
            as castling rights.
        """
        # If no moves have been played, do nothing
        if len(self.history) <= 1:
            return
        
        # Get and restore position properties
        properties: PositionProperties = self.history.pop()
        self.game_state = properties.game_state
        self.turn = properties.turn
        self.castle_rights = properties.castle_rights
        self.en_passant = properties.en_passant
        self.halfmove_clock = properties.halfmove_clock
        self.fullmove_count = properties.fullmove_count
        self.zbr = properties.zbr

        move: Move = properties.move

        # Get from/to masks
        if move.from_index is not None:
            from_mask = squares.masks[move.from_index]
        if move.to_index is not None:
            to_mask = squares.masks[move.to_index]

        # Quiet moves
        if move.move_type == MoveType.QUIET:
            # Move the piece back
            self.__move_piece(move.to_index, move.from_index, move.piece)
        # Double pawn moves
        elif move.move_type == MoveType.DOUBLE_PAWN:
            # Move the piece back
            self.__move_piece(move.to_index, move.from_index, move.piece)
        # Captures
        elif move.move_type == MoveType.CAPTURE:
            # Move the piece back
            self.__move_piece(move.to_index, move.from_index, move.piece)
            # Replace the captured piece
            self.__add_piece(move.to_index, opposing_side(self.turn), properties.capture)
        # Promotions
        elif move.move_type == MoveType.PROMOTION:
            # Move the piece back and turn it back to a pawn
            self.__move_and_change_piece(
                move.to_index,
                move.from_index,
                move.promotion,
                PieceType.PAWN
            )
        # En Passant
        elif move.move_type == MoveType.EN_PASSANT:
            capture_mask = \
                utils.south(to_mask) if self.turn == Side.WHITE \
                else utils.north(to_mask)
            capture_index = utils.ls1b_index(capture_mask)
            # Move the pawn back and return the captured piece
            self.__move_piece(move.to_index, move.from_index, move.piece)
            self.__add_piece(capture_index, opposing_side(self.turn), properties.capture)
        # Capture promotions
        elif move.move_type == MoveType.CAPTURE_PROMOTION:
            # Move the promoted piece back and turn it back to a pawn
            self.__move_and_change_piece(
                move.to_index,
                move.from_index,
                move.promotion,
                PieceType.PAWN
            )
            # Return the captured piece
            self.__add_piece(move.to_index, opposing_side(self.turn), properties.capture)
        # Kingside Castling
        elif move.move_type == MoveType.CASTLE_KINGSIDE:
            if self.turn == Side.WHITE:
                self.__move_piece(squares.g1, squares.e1, PieceType.KING)
                self.__move_piece(squares.f1, squares.h1, PieceType.ROOK)
            elif self.turn == Side.BLACK:
                self.__move_piece(squares.g8, squares.e8, PieceType.KING)
                self.__move_piece(squares.f8, squares.h8, PieceType.ROOK)
        # Queenside Castling
        elif move.move_type == MoveType.CASTLE_QUEENSIDE:
            if self.turn == Side.WHITE:
                self.__move_piece(squares.c1, squares.e1, PieceType.KING)
                self.__move_piece(squares.d1, squares.a1, PieceType.ROOK)
            elif self.turn == Side.BLACK:
                self.__move_piece(squares.c8, squares.e8, PieceType.KING)
                self.__move_piece(squares.d8, squares.a8, PieceType.ROOK)
        # Duck moves
        elif move.move_type == MoveType.DUCK:
            self.boards.duck = to_mask

        # Update occupied board
        self.boards.occupied = self.boards.white | self.boards.black | self.boards.duck

    def recalculate_mailbox(self):
        """ Returns a freshly calculated mailbox representation
            of the board state.
        """
        result = [Piece.EMPTY] * 64
        for piece, board in self.boards.pieces[Side.WHITE].items():
            for square in utils.get_squares(board):
                result[square] = piece | Side.WHITE

        for piece, board in self.boards.pieces[Side.BLACK].items():
            for square in utils.get_squares(board):
                result[square] = piece | Side.BLACK
        
        return result

    def __str__(self):
        state = [p for p in self.mailbox]
        if self.boards.duck:
            state[utils.get_squares(self.boards.duck)[0]] = Piece.DUCK
        result = ""
        for s in range(len(state), 0, -8):
            result += f"{s//8}|" \
                + ''.join([pieces.symbols[p] for p in state[s-8:s]]) \
                + '\n'
        result += " +--------\n  ABCDEFGH"
        return result
