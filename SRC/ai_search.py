import copy
from ai_eval import eval_board

INF = float("inf")
#generate all legal moves for color
def get_moves(board,color):
    all_moves = []

    for row in range(8):
        for col in range(8):
            square = board.squares[row][col]
            #check if a piece exist on square
            if square.has_piece():
                piece = square.piece
                
                if piece.color == color:
                    piece.clear_moves()
                    board.moves_calc(piece, row, col, bool = True)
                    for move in piece.moves: 
                        all_moves.append((piece, move, row, col))
    return all_moves
#negamax seearch 
def negamax(board, depth,alpha, beta, color_sign):
    #base has eval board when depth is 0
    if depth == 0:
            return color_sign * eval_board(board)
    
    color = "white" if color_sign == 1 else "black"
    moves = get_moves(board, color)
    #if no given moves then eval the given board
    if not moves:
         return color_sign * eval_board(board)
    
    best_score = float("-inf")
    for piece, move, row, col in moves:
         temp_board = copy.deepcopy(board) 
         temp_piece = temp_board.squares[row][col].piece

         temp_board.move(temp_piece, move)
         #recursive method for negamax
         score = -negamax(temp_board, depth - 1, -beta, -alpha, -color_sign)

         if score > best_score:
              best_score = score
              #alpha bound update
         if score > alpha:
              alpha = score
              #stop searching bad case
         if alpha >= beta:
              break
    return best_score
