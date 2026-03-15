import copy
from SRC.ai_search import get_moves, negamax

class AIPlayer:
    def __init__(self, color="black", depth=2):
        self.color = color
        self.depth = depth

    def choose_move(self, board):
        best_move = None
        best_score = float("-inf")
        #determines color sign pos(white) or neg(black)
        color_sign = 1 if self.color == "white" else -1
        #Alpha-beta startin bounds
        alpha = float("-inf")
        beta = float("inf")
        #generates all possible moves
        all_moves = get_moves(board, self.color)

        for piece, move, row, col in all_moves:
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.squares[row][col].piece

            temp_board.move(temp_piece, move)
            #evaluate score based on the negamax 
            score= -negamax(temp_board, self.depth -1, -beta, -alpha, -color_sign)
            #update best move when better score
            if score> best_score:
                best_score = score
                best_move = (move, row, col)
            #update alpha bound
            if score > alpha:
                alpha = score
        return best_move