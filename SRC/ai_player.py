import copy
import random
from ai_search import get_moves, negamax

class AIPlayer:
    def __init__(self, color="black", depth=3):
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
            board.make_move(piece, move)
            if board.is_in_check(self.color):
                board.unmake_move()
                continue

            score = -negamax(board, self.depth, -beta, -alpha, -color_sign)
            board.unmake_move()
            scored_moves.append((score,move,row,col))

            if score>alpha:
                alpha = score
        if not scored_moves:
            return None
        
        scored_moves.sort(key=lambda x: x[0],reverse = True)
        best_score = scored_moves[0][0]
        if board.move_count < 6:
            possible_moves = [m for m in scored_moves if m[0] >= best_score - 10]
            score, move, row, col = random.choice(possible_moves)
        else:
            score, move, row, col = scored_moves[0]
        return(move, row, col)
        