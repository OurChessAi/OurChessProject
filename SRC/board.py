from square import Square
from dimensions import *
from piece import *
from moves import Move
from sound import  Sound
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

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col]=Square(row,col)

    def _add_pieces(self, color):
        row_pawn, row_other =(6, 7) if color =='white' else (1, 0)


        #pawns
        for col in range(COLS):
            self.squares[row_pawn][col]=Square(row_pawn, col, Pawn(color))



        #knights
        self.squares[row_other][1] = Square(row_other, 1,Knight(color))
        self.squares[row_other][6] = Square(row_other, 6,Knight(color))

        #Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))


        #Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))


        #King
        self.squares[row_other][4] = Square(row_other, 4, King(color))


    def move(self, piece, move, passanting = False):
        first = move.first
        final = move.final

        en_passant_empty =self.squares[final.row][final.col].isempty()

     # board gui move update
        self.squares[first.row][first.col].piece = None
        self.squares[final.row][final.col].piece = piece






        if isinstance(piece, Pawn):
            difference = final.col - first.col
            if difference != 0 and en_passant_empty:
                # board gui move update
                self.squares[first.row][first.col + difference].piece = None
                self.squares[final.row][final.col].piece = piece
                if not passanting:
                    sound =  Sound(
                            os.path.join('assets/sounds/capture.wav'))
                    sound.play()



            # pawn promotion
            else:
                self.check_promotion(piece, final)

        #king castling
        if isinstance(piece, King):
            if self.castling(first, final):
                diff = final.col - first.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])


        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #set last move
        self.last_move = move
        self.move_count += 1

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row== 7:
            self.squares [final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self,piece, move):
        temp_piece = copy.copy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece,move,passanting = True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_opp_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.moves_calc(p, row, col, bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True

        return False

    def set_true_en_passant(self, piece, move):
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        if isinstance(piece, Pawn):
            if abs(move.final.row - move.first.row) == 2:
                piece.en_passant = True





    def moves_calc(self,piece, row, col, bool = True):
        """ Determine the valid moves of a piece on a specific square """


        def pawn_move():
            # the steps a pawn can make
            steps = 1 if piece.moved else 2

            #vertical steps
            start = row + piece.dir
            end = row + (piece.dir *(1+steps))
            for move_row in range(start, end,piece.dir):
                if Square.in_range(move_row):
                    if self.squares [move_row][col].isempty():
                      # create first and final move squares
                        first_pos = Square(row,col)
                        final_pos = Square(move_row,col)
                      # create new move
                        move = Move(first_pos,final_pos)
                      # check potential check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)

                        else:
                            piece.add_move(move)
                    # block
                    else:
                        break
                # not in range
                else:
                    break


            # diagonal moves
            move_row = row + piece.dir
            move_cols = [col-1, col+1]
            for move_col in move_cols:
                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].has_opp_piece(piece.color):
                        # create first and final move squares
                        first = Square(row,col)
                        #checks
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row,move_col,final_piece)
                        # create new move
                        move = Move(first,final)
                        # check potential check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)

                        else:
                            piece.add_move(move)
            # en passant
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            #left en passant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_opp_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create first and final move squares
                            first = Square(row, col)
                            final = Square(fr, col-1, p)
                            # create new move
                            move = Move(first, final)
                            # check potential check
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)

                            else:
                                piece.add_move(move)

                            # right en passant
            if Square.in_range(col + 1) and row == r:
                 if self.squares[row][col + 1].has_opp_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create first and final move squares
                            first = Square(row, col)
                            final = Square(fr, col + 1, p)
                            # create new move
                            move = Move(first, final)
                            # check potential check
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)

                            else:
                                piece.add_move(move)

        def knight_move():
            # 8 moves are possible
            poss_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),

            ]

            for poss_move in poss_moves:
                poss_move_row,poss_move_col = poss_move

                if Square.in_range(poss_move_row, poss_move_col):
                    if self.squares[poss_move_row] [poss_move_col].isempty_or_opp(piece.color):
                        # Square creation for the new move
                        initial = Square(row, col)
                        final_piece = self.squares[poss_move_row][poss_move_col].piece
                        final = Square(poss_move_row, poss_move_col,final_piece)
                        # new move creation
                        move = Move(initial,final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break

                        else:
                            piece.add_move(move)


        def straight_moves(incr):
            for inc in incr:
                row_inc, col_inc = inc
                move_row = row + row_inc
                move_col = col + col_inc


                while True:
                    if Square.in_range(move_row, move_col):
                        #create squares for poss moves
                        first = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row,move_col, final_piece)
                        # create a possible new move
                        move = Move(first,final)

                        # if empty continue iteration
                        if self.squares[move_row][move_col].isempty():
                            #check potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)


                            else:
                                piece.add_move(move)

                        # if has opp piece then add move + break
                        elif self.squares[move_row][move_col].has_opp_piece(piece.color):
                            # check potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)


                            else:
                                piece.add_move(move)
                            break


                        # if ally piece then break
                        elif self.squares[move_row][move_col].has_team_piece(piece.color):
                            break
                    # not in range
                    else: break
                    #incrementing the increments
                    move_row = move_row + row_inc
                    move_col = move_col + col_inc


        def king_move():
            adjacents= [
                (row-1, col+0), #up
                (row-1, col+1), #up-right
                (row+0, col+1), # right
                (row+1, col+1), # d-right
                (row+1, col+0), # down
                (row+1, col-1), # d-left
                (row+0, col-1), # left
                (row-1, col-1), # up-left

            ]
            for king_move in adjacents:
                king_move_row, king_move_col = king_move

                if Square.in_range(king_move_row, king_move_col):
                    if self.squares[king_move_row][king_move_col].isempty_or_opp(piece.color):
                        # Square creation for the new move
                        initial = Square(row, col)
                        final = Square(king_move_row, king_move_col)
                        # new move creation
                        move = Move(initial, final)
                        # check potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else : break


                        else:
                            piece.add_move(move)
                    # Castling
                if not piece.moved:
                    # Queen Castling
                    left_rook = self.squares[row][0].piece
                    if isinstance(left_rook, Rook):
                        if not left_rook.moved:
                            for c in range(1, 4):
                                # castling can't be done due to the pieces in between
                                if self.squares[row][c].has_piece():
                                    break

                                if c == 3:
                                    # adds left rook to king
                                    piece.left_rook = left_rook

                                    # rook move
                                    initial = Square(row, 0)
                                    final = Square(row, 3)
                                    moveR = Move(initial, final)
                                    left_rook.add_move(moveR)

                                    # king move
                                    initial = Square(row, col)
                                    final = Square(row, 2)
                                    moveK = Move(initial, final)
                                    piece.add_move(moveK)
                                    # check potential checks
                                    if bool:
                                        if not self.in_check(piece, move) and not self.in_check(left_rook, moveR):
                                            #add new move to rook
                                            left_rook.add_move(moveR)
                                            #add new move to king
                                            piece.add_move(moveK)


                                    else:
                                        # add new move to rook
                                        left_rook.add_move(moveR)
                                        # add new move to king

                                        piece.add_move(moveK)
                    # King Castling
                    right_rook = self.squares[row][7].piece
                    if isinstance(right_rook, Rook):
                        if not right_rook.moved:
                            for c in range(5, 7):
                                # castling can't be done due to the pieces in between
                                if self.squares[row][c].has_piece():
                                    break

                                if c == 6:
                                    # adds right rook to king
                                    piece.right_rook = right_rook

                                    # rook move
                                    initial = Square(row, 7)
                                    final = Square(row, 5)
                                    moveR = Move(initial, final)


                                    # king move
                                    initial = Square(row, col)
                                    final = Square(row, 6)
                                    moveK = Move(initial, final)
                                    if bool:
                                        if not self.in_check(piece, move) and not self.in_check(right_rook, moveR):
                                            # add new move to rook
                                            right_rook.add_move(moveR)
                                            # add new move to king
                                            piece.add_move(moveK)


                                    else:
                                        # add new move to rook
                                        right_rook.add_move(moveR)
                                        # add new move to king

                                        piece.add_move(moveK)


        if isinstance(piece, Pawn):
            pawn_move()

        elif isinstance(piece, Bishop):
            straight_moves([
                (-1, 1),# upper right
                (-1, -1),# up left
                ( 1, 1 ), # down right
                ( 1, -1) # d left

            ])

        elif isinstance(piece, Knight):
            knight_move()

        elif isinstance(piece, Rook):
            straight_moves([
                (-1, 0), #up
                (0, 1), # right
                (1, 0 ), # down
                (0, -1) #left
            ])

        elif isinstance(piece, Queen):
            straight_moves([
                    (-1, 1),  # upper right
                    (-1, -1),  # up left
                    (1, 1),  # down right
                    (1, -1),  # d left
                    (-1, 0),  # up
                    (0, 1),  # right
                    (1, 0),  # down
                    (0, -1)  # left

                ]
            )

        elif isinstance(piece, King):king_move()