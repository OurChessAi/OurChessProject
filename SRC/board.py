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
        self.move_count = 0
        self.history = []

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
        self.move_count += 1

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    # Refactor to use is_in_check; since moves_calc calls this, loop can desync
    def in_check(self, piece, move):
        self.make_move(piece,move)
        in_check = self.is_in_check(piece.color)
        self.unmake_move()
        return in_check

    # Cleanup: track pos of king, then check if opp moves can attack it
    def is_in_check(self, color):
        """Check if the king of 'color' is currently under attack on this board."""
        # Find king pos
        king_pos = None
        for r in range(8):
            for c in range(8):
                sq = self.squares[r][c]
                if sq.has_piece() and isinstance(sq.piece, King) and sq.piece.color == color:
                    king_pos = (r, c)
                    break

        if not king_pos:
            return False
        
        # Check if opp piece can hit the king
        for r in range(8):
            for c in range(8):
                if self.squares[r][c].has_opp_piece(color):
                    p = self.squares[r][c].piece
                    # Temp move list
                    self.moves_calc(p, r, c, bool=False)

                    for m in p.moves:
                        if (m.final.row, m.final.col) == king_pos:
                            p.clear_moves() #clean up
                            return True
                        
                    p.clear_moves() #clean up
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

        # Addition of a helper function to validate and add moves
        def _append_move(first, final):
            move = Move(first, final)
            if bool:
                if not self.in_check(piece, move):
                    piece.add_move(move)
            else:
                piece.add_move(move)

        # Clean structure with helper function
        def pawn_move():
            # the steps a pawn can make
            steps = 1 if piece.moved else 2

            # vertical steps
            start = row + piece.dir
            end   = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        _append_move(Square(row, col), Square(move_row, col))
                    else:
                        # Square empty
                        break
                else:
                    break

            # diagonal captures
            move_row  = row + piece.dir
            move_cols = [col - 1, col + 1]
            for move_col in move_cols:
                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].has_opp_piece(piece.color):
                        _append_move(Square(row, col), Square(move_row, move_col, self.squares[move_row][move_col].piece))

            # en passant
            r  = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5

            # left en passant
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col - 1].has_opp_piece(piece.color):
                    p = self.squares[row][col - 1].piece
                    if isinstance(p, Pawn) and p.en_passant:
                        _append_move(Square(row, col), Square(fr, col - 1))

            # right en passant
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_opp_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn) and p.en_passant:
                        _append_move(Square(row, col), Square(fr, col + 1))

        # Clean up to use helper
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
                        _append_move(Square(row, col), Square(poss_move_row, poss_move_col, self.squares[poss_move_row][poss_move_col].piece))

        # Clean up to use helper
        def straight_moves(incr):
            for inc in incr:
                row_inc, col_inc = inc
                move_row = row + row_inc
                move_col = col + col_inc

                while Square.in_range(move_row, move_col):
                    sq = self.squares[move_row][move_col]
                    final = Square(move_row, move_col, sq.piece)

                    if sq.isempty():
                        _append_move(Square(row, col), final)

                    elif sq.has_opp_piece(piece.color):
                        _append_move(Square(row, col), final)
                        break

                    else:   # Team piece
                        break

                    move_row += row_inc
                    move_col += col_inc

        # Add helper, and castling overhaul
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
                        _append_move(Square(row, col), Square(km_row, km_col))

            # Castling
            if not piece.moved:
                # Check because can't castle out of check
                if bool and self.is_in_check(piece.color):
                    return
                
                # Queen-side castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook) and not left_rook.moved:
                    if all(not self.squares[row][c].has_piece() for c in range(1, 4)):
                        # Check if squre the king passes through is safe
                        pass_through = Move(Square(row, col), Square(row, 3))
                        # Check if landing is safe
                        landing = Move(Square(row, col), Square(row, 2))

                        if bool:
                            if not self.in_check(piece, pass_through) and not self.in_check(piece, landing):
                                piece.add_move(landing)
                        else:
                            piece.add_move(landing)

                # King-side castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook) and not right_rook.moved:
                    if all(not self.squares[row][c].has_piece() for c in range(5, 7)):
                        # Check if squre the king passes through is safe
                        pass_through = Move(Square(row, col), Square(row, 5))
                        # Check if landing is safe
                        landing = Move(Square(row, col), Square(row, 6))

                        if bool:
                            if not self.in_check(piece, pass_through) and not self.in_check(piece, landing):
                                piece.add_move(landing)
                        else:
                            piece.add_move(landing)

        # Clearing moves to ensure we start with a clean slate
        piece.clear_moves()

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
    def make_move(self, piece, move):
        captured = self.squares[move.final.row][move.final.col].piece

        self.history.append((
            piece,
            move.first.row, move.first.col,
            move.final.row, move.final.col,
            captured,
            piece.moved
        ))

        self.squares[move.first.row][move.first.col].piece = None
        self.squares[move.final.row][move.final.col].piece = piece
        piece.moved = True
    def unmake_move(self):
        piece, oldR, oldC, newR, newC, captured, was_moved = self.history.pop()
        self.squares[newR][newC].piece = None
        self.squares[oldR][oldC].piece = piece
        piece.moved = was_moved
        if captured:
            self.squares[newR][newC].piece = captured