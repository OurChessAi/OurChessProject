from sound import Sound
from square import Square
from dimensions import *
from piece import *
from moves import Move
from sound import Sound
import copy
import os


class Board:
    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color))

    def move(self, piece, move, passanting=False):
        first = move.first
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # board gui move update
        self.squares[first.row][first.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            difference = final.col - first.col
            if difference != 0 and en_passant_empty:
                # en passant capture
                self.squares[first.row][first.col + difference].piece = None
                self.squares[final.row][final.col].piece = piece
                if not passanting:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            else:
                # pawn promotion
                self.check_promotion(piece, final)

        # king castling
        if isinstance(piece, King):
            if self.castling(first, final):
                diff = final.col - first.col
                # FIX: compute rook positions directly instead of using
                # rook.moves[-1] which crashes if moves were cleared
                if diff < 0:
                    rook_from_col = 0  # queen-side
                    rook_to_col   = 3
                else:
                    rook_from_col = 7  # king-side
                    rook_to_col   = 5

                rook = self.squares[first.row][rook_from_col].piece
                if rook is not None:
                    self.squares[first.row][rook_from_col].piece = None
                    self.squares[first.row][rook_to_col].piece   = rook
                    rook.moved = True
                    rook.clear_moves()

        # mark piece as moved
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self, piece, move):
        temp_piece = copy.copy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, passanting=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_opp_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.moves_calc(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def is_in_check(self, color):
        """Check if the king of 'color' is currently under attack on this board."""
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_opp_piece(color):
                    p = self.squares[row][col].piece
                    p.clear_moves()
                    self.moves_calc(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        return False

    def has_legal_moves(self, color):
        """Return True if the player of 'color' has at least one legal move."""
        for row in range(ROWS):
            for col in range(COLS):
                sq = self.squares[row][col]
                if sq.has_piece() and sq.piece.color == color:
                    sq.piece.clear_moves()
                    self.moves_calc(sq.piece, row, col, bool=True)
                    if sq.piece.moves:
                        sq.piece.clear_moves()
                        return True
        return False

    def is_checkmate(self, color):
        """Return True if 'color' is in checkmate (in check AND no legal moves)."""
        return self.is_in_check(color) and not self.has_legal_moves(color)

    def is_stalemate(self, color):
        """Return True if 'color' is in stalemate (NOT in check AND no legal moves)."""
        return not self.is_in_check(color) and not self.has_legal_moves(color)

    def set_true_en_passant(self, piece, move):
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        if isinstance(piece, Pawn):
            if abs(move.final.row - move.first.row) == 2:
                piece.en_passant = True

    def moves_calc(self, piece, row, col, bool=True):
        """Determine the valid moves of a piece on a specific square."""

        def pawn_move():
            # the steps a pawn can make
            steps = 1 if piece.moved else 2

            # vertical steps
            start = row + piece.dir
            end   = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        first_pos = Square(row, col)
                        final_pos = Square(move_row, col)
                        move = Move(first_pos, final_pos)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    else:
                        break
                else:
                    break

            # diagonal captures
            move_row  = row + piece.dir
            move_cols = [col - 1, col + 1]
            for move_col in move_cols:
                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].has_opp_piece(piece.color):
                        first       = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final       = Square(move_row, move_col, final_piece)
                        move = Move(first, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # en passant
            r  = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5

            # left en passant
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col - 1].has_opp_piece(piece.color):
                    p = self.squares[row][col - 1].piece
                    if isinstance(p, Pawn) and p.en_passant:
                        first = Square(row, col)
                        final = Square(fr, col - 1, p)
                        move  = Move(first, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # right en passant
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_opp_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn) and p.en_passant:
                        first = Square(row, col)
                        final = Square(fr, col + 1, p)
                        move  = Move(first, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

        def knight_move():
            poss_moves = [
                (row - 2, col + 1),
                (row - 1, col + 2),
                (row + 1, col + 2),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row + 1, col - 2),
                (row - 1, col - 2),
                (row - 2, col - 1),
            ]
            for poss_move in poss_moves:
                poss_move_row, poss_move_col = poss_move
                if Square.in_range(poss_move_row, poss_move_col):
                    if self.squares[poss_move_row][poss_move_col].isempty_or_opp(piece.color):
                        initial     = Square(row, col)
                        final_piece = self.squares[poss_move_row][poss_move_col].piece
                        final       = Square(poss_move_row, poss_move_col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

        def straight_moves(incr):
            for inc in incr:
                row_inc, col_inc = inc
                move_row = row + row_inc
                move_col = col + col_inc

                while True:
                    if Square.in_range(move_row, move_col):
                        first       = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final       = Square(move_row, move_col, final_piece)
                        move = Move(first, final)

                        if self.squares[move_row][move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        elif self.squares[move_row][move_col].has_opp_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        elif self.squares[move_row][move_col].has_team_piece(piece.color):
                            break
                    else:
                        break

                    move_row += row_inc
                    move_col += col_inc

        def king_move():
            adjacents = [
                (row - 1, col + 0),  # up
                (row - 1, col + 1),  # up-right
                (row + 0, col + 1),  # right
                (row + 1, col + 1),  # d-right
                (row + 1, col + 0),  # down
                (row + 1, col - 1),  # d-left
                (row + 0, col - 1),  # left
                (row - 1, col - 1),  # up-left
            ]
            for km in adjacents:
                km_row, km_col = km
                if Square.in_range(km_row, km_col):
                    if self.squares[km_row][km_col].isempty_or_opp(piece.color):
                        initial = Square(row, col)
                        final   = Square(km_row, km_col)
                        move    = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # Castling
            if not piece.moved:
                # Queen-side castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook) and not left_rook.moved:
                    path_clear = all(
                        not self.squares[row][c].has_piece() for c in range(1, 4)
                    )
                    if path_clear:
                        piece.left_rook = left_rook
                        moveR = Move(Square(row, 0), Square(row, 3))
                        left_rook.add_move(moveR)
                        moveK = Move(Square(row, col), Square(row, 2))
                        if bool:
                            king_safe = (
                                not self.in_check(piece, moveK) and
                                not self.in_check(piece, Move(Square(row, col), Square(row, 3)))
                            )
                            if king_safe:
                                piece.add_move(moveK)
                            else:
                                left_rook.clear_moves()
                        else:
                            piece.add_move(moveK)

                # King-side castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook) and not right_rook.moved:
                    path_clear = all(
                        not self.squares[row][c].has_piece() for c in range(5, 7)
                    )
                    if path_clear:
                        piece.right_rook = right_rook
                        moveR = Move(Square(row, 7), Square(row, 5))
                        right_rook.add_move(moveR)
                        moveK = Move(Square(row, col), Square(row, 6))
                        if bool:
                            king_safe = (
                                not self.in_check(piece, moveK) and
                                not self.in_check(piece, Move(Square(row, col), Square(row, 5)))
                            )
                            if king_safe:
                                piece.add_move(moveK)
                            else:
                                right_rook.clear_moves()
                        else:
                            piece.add_move(moveK)

        if isinstance(piece, Pawn):
            pawn_move()
        elif isinstance(piece, Bishop):
            straight_moves([(-1, 1), (-1, -1), (1, 1), (1, -1)])
        elif isinstance(piece, Knight):
            knight_move()
        elif isinstance(piece, Rook):
            straight_moves([(-1, 0), (0, 1), (1, 0), (0, -1)])
        elif isinstance(piece, Queen):
            straight_moves([(-1, 1), (-1, -1), (1, 1), (1, -1),
                            (-1, 0), (0, 1),  (1, 0), (0, -1)])
        elif isinstance(piece, King):
            king_move()
