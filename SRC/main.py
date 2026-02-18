# This is the main file for the chess game
import pygame
import sys

from SRC.board import Board
from jeu import Jeu

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
            game.show_pieces(screen)

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
                        drag.save_initial(event.pos)
                        drag.drag_piece(piece)
                #mouse motion
                elif event.type == pygame.MOUSEMOTION:

                    if drag.dragging:
                        drag.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_pieces(screen)
                        drag.update_blit(screen)

                #click release
                elif  event.type  == pygame.MOUSEBUTTONUP:
                    drag.undrag_piece()

                #End App
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

main = Main()
main.mainloop()