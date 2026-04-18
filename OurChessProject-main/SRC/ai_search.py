import copy
from ai_eval import eval_board, get_val

INF = float("inf")
#generate all legal moves for color
def score_move(board, piece, move):
    score= 0
    target = board.squares[move.final.row][move.final.col].piece
    if target:
        score += 10 * get_val(target) - get_val(piece)
    return score
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
    all_moves.sort(key=lambda x: score_move(board, x[0],x[1]), reverse = True)
    return all_moves

def qSearch(board, alpha, beta, color_sign):
    sp = color_sign * eval_board(board)
    if sp >= beta:
        return beta
    if sp > alpha:
        alpha = sp
    color = "white" if color_sign == 1 else "black"
    moves = get_moves(board, color)
    captures = [(p,m,r,c) for p, m, r, c in moves
                if board.squares[m.final.row][m.final.col].piece]
    for piece, move, row, col in captures:
        board.make_move(piece, move)
        if board.is_in_check(color):
            board.unmake_move()
            continue
        score = -qSearch(board, -beta, -alpha, -color_sign)
        board.unmake_move()
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break
    return alpha

#negamax seearch 
def negamax(board, depth,alpha, beta, color_sign):
    #base has eval board when depth is 0
    if depth == 0:
        return qSearch(board, alpha, beta, color_sign)
    color = "white" if color_sign == 1 else "black"
    moves = get_moves(board, color)

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