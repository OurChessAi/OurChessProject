from square import Square
from dimensions import *
from piece import *
from moves import Move

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


    def move(self, piece, move):
        first = move.first
        final = move.final

     # board gui move update
        self.squares[first.row][first.col].piece = None
        self.squares[final.row][final.col].piece = piece

        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves



    def moves_calc(self,piece, row, col):
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
                        final = Square(move_row,move_col)
                        # create new move
                        move = Move(first,final)
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
                        final = Square(poss_move_row, poss_move_col)
                        # new move creation
                        move = Move(initial,final)
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
                        final = Square(move_row,move_col)
                        # create a possible new move
                        move = Move(first,final)

                        # if empty continue iteration
                        if self.squares[move_row][move_col].isempty():
                            #create new move
                            piece.add_move(move)

                        # if has opp piece then add move + break
                        if self.squares[move_row][move_col].has_opp_piece(piece.color):
                            piece.add_move(move)
                            break


                        # if ally piece then break
                        if self.squares[move_row][move_col].has_team_piece(piece.color):
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
                        piece.add_move(move)








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