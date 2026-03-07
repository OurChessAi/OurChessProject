# This is the main file for the chess game
import pygame
import sys

from board import Board
from square import Square
from jeu import Jeu
from moves import Move


from dimensions import *

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Best Chess Game Ever')
        self.jeu = Jeu()

    def mainloop(self):
        screen = self.screen
        game = self.jeu
        board = self.jeu.board
        drag = self.jeu.drag
        while True:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if drag.dragging:
                drag.update_blit(screen)

            for event in pygame.event.get():
                #Click Events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    drag.update_mouse(event.pos)
                    clicked_row = drag.mouseY // SQSIZE
                    clicked_col = drag.mouseX // SQSIZE

                    #does the clicked square has a piece?
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        # valid piece (color)
                        if piece.color == game.next_player:
                            board.moves_calc(piece, clicked_row, clicked_col)
                            drag.save_initial(event.pos)
                            drag.drag_piece(piece)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.show_pieces(screen)

                #mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE
                    game.set_hover(motion_row, motion_col)

                    if drag.dragging:
                        drag.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        drag.update_blit(screen)

                #click release
                elif  event.type  == pygame.MOUSEBUTTONUP:
                    if drag.dragging:
                        drag.update_mouse(event.pos)
                        released_row = drag.mouseY // SQSIZE
                        released_col = drag.mouseX // SQSIZE

                        # create valid move
                        first = Square(drag.initial_row,drag.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(first, final)

                        # is it a valid move?
                        if board.valid_move(drag.piece, move):
                            board.move(drag.piece, move)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            #next turn
                            game.next_turn()

                    drag.undrag_piece()

                #End App
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

main = Main()
main.mainloop()