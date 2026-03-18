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
        game  = self.jeu
        board = self.jeu.board
        drag  = self.jeu.drag

        while True:
            # ── always draw the board ────────────────────────────────────────
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if drag.dragging:
                drag.update_blit(screen)

            # ── if the game is over, draw overlay and handle its buttons ─────
            if game.game_over:
                restart_rect, close_rect = game.show_game_over(screen)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_rect.collidepoint(event.pos):
                            # restart the whole game
                            game.restart()
                            game  = self.jeu
                            board = self.jeu.board
                            drag  = self.jeu.drag

                        elif close_rect.collidepoint(event.pos):
                            pygame.quit()
                            sys.exit()

                pygame.display.update()
                continue   # skip normal event handling while overlay is visible

            # ── normal gameplay event loop ───────────────────────────────────
            for event in pygame.event.get():

                # Click Events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    drag.update_mouse(event.pos)

                    # Bug #1 fix: clamp to board range to prevent out-of-bounds crash
                    clicked_row = min(drag.mouseY // SQSIZE, ROWS - 1)
                    clicked_col = min(drag.mouseX // SQSIZE, COLS - 1)

                    # does the clicked square have a piece?
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        # valid piece (color)
                        if piece.color == game.next_player:
                            board.moves_calc(piece, clicked_row, clicked_col, bool=True)
                            drag.save_initial(event.pos)
                            drag.drag_piece(piece)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    # Bug #1 fix: clamp motion row/col to board range
                    motion_row = min(event.pos[1] // SQSIZE, ROWS - 1)
                    motion_col = min(event.pos[0] // SQSIZE, COLS - 1)
                    game.set_hover(motion_row, motion_col)

                    if drag.dragging:
                        drag.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        drag.update_blit(screen)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    if drag.dragging:
                        drag.update_mouse(event.pos)

                        # Bug #1 fix: clamp released row/col to board range
                        released_row = min(drag.mouseY // SQSIZE, ROWS - 1)
                        released_col = min(drag.mouseX // SQSIZE, COLS - 1)

                        # create valid move
                        first = Square(drag.initial_row, drag.initial_col)
                        final = Square(released_row, released_col)
                        move  = Move(first, final)

                        # is it a valid move?
                        if board.valid_move(drag.piece, move):
                            # normal capture?
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(drag.piece, move)

                            board.set_true_en_passant(drag.piece, move)
                            # sounds
                            game.play_sound(captured)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            # next turn
                            game.next_turn()

                            # ── check for checkmate / stalemate ─────────────
                            game.check_game_over()

                    drag.undrag_piece()

                # kb presses
                elif event.type == pygame.KEYDOWN:
                    # switch themes
                    if event.key == pygame.K_t:
                        game.change_theme()

                    # restart
                    if event.key == pygame.K_r:
                        game.restart()
                        game  = self.jeu
                        board = self.jeu.board
                        drag  = self.jeu.drag

                # End App
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


main = Main()
main.mainloop()
