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
                    board.moves_calc(piece, row, col, bool = False)
                    for move in piece.moves: 
                        all_moves.append((piece, move, row, col))
    return all_moves
#negamax seearch 
def negamax(board, depth,alpha, beta, color_sign):
    print("NEGAMAX CALLED WITH DEPTH =", depth)
    #base has eval board when depth is 0
    if depth == 0:
        return color_sign * eval_board(board)
    color = "white" if color_sign == 1 else "black"
    moves = get_moves(board, "white" if color_sign == 1 else "black")

    if not moves:
        return color_sign * eval_board(board)
    for piece, move, row, col in moves:
        board.make_move(piece, move)
        if board.is_in_check(color):
            board.unmake_move()
            continue
        score = -negamax(board, depth - 1, -beta, -alpha, -color_sign)
        board.unmake_move()

        if score> alpha:
            alpha = score
        if alpha >= beta:
            break
    return alpha