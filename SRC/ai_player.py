import copy
import random
from ai_search import get_moves, negamax

class AIPlayer:
    def __init__(self, color="black", depth=4):
        self.color = color
        self.depth = depth

    def choose_move(self, board):
        scored_moves = []
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
            scored_moves.append((score, move, row, col))
            if score > alpha:
                alpha = score
        if not scored_moves:
            return None
        
        scored_moves.sort(key=lambda x: x[0],reverse = True)
        best_score = scored_moves[0][0]

        possible_moves = [m for m in scored_moves if m[0] >= best_score - 25]
        score, move, row, col = random.choice(possible_moves)
        return(move, row, col)
        