from piece import Pawn, Knight, Bishop, Rook, Queen, King
from piece_tables import *

PIECE_VALS = {
    Pawn: 100,
    Knight: 320,
    Bishop: 330,
    Rook: 500,
    Queen: 900,
    King: 20000,
}



#returns base material value of piece
def get_val(piece):
    for piece_type, val in PIECE_VALS.items():
        if isinstance(piece,piece_type):
            return val
    return 0
#material and positional strenth of each square 
#Pos values favor white Neg values favor black
def eval_board(board):
    score = 0

    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]

            #does square have piece
            if square.has_piece():
                piece = square.piece
                value = get_val(piece)

                table_row = row if piece.color == "white" else 7 - row
                bonus = 0
                #positional bonuses
                if isinstance(piece,Pawn):
                    bonus = PAWN_TABLE[table_row][col]
                elif isinstance(piece,Knight):
                    bonus = KNIGHT_TABLE[table_row][col]
                elif isinstance(piece,Bishop):
                    bonus = BISHOP_TABLE[table_row][col]
                elif isinstance(piece,Rook):
                    bonus = ROOK_TABLE[table_row][col]
                elif isinstance(piece,Queen):
                    bonus = QUEEN_TABLE[table_row][col]

                value += bonus *10
                #add or subtract score based on if white or black
                if piece.color == "white":
                    score += value
                else:
                    score -= value
    return score
