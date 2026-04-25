# This is the main file for the chess game
import pygame
import sys

from board import Board
from square import Square
from jeu import Jeu
from moves import Move
from ai_player import AIPlayer

from dimensions import *


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Best Chess Game Ever')
        self.jeu = Jeu()
        # Add a menu state to differentiate between menu and game
        self.state = "menu"
        # Wait for update from menu
        self.ai = None
        self.pending_ai = False

    def mainloop(self):
        while True:
            if self.state == "menu":
                self.show_menu()
            elif self.state == "game":
                self.run_game()

    # Moved from while True; game loop
    def run_game(self):
        screen = self.screen
        game  = self.jeu
        board = self.jeu.board
        drag = self.jeu.drag
        # ── always draw the board ────────────────────────────────────────
        game.show_bg(screen)
        game.show_last_move(screen)
        game.show_moves(screen)
        game.show_pieces(screen)
        game.show_hover(screen)
        
        if self.pending_ai and self.ai and game.next_player == self.ai.color:
            pygame.display.update()

            ai_choice = self.ai.choose_move(board)

            if ai_choice:
                ai_move, ai_row, ai_col = ai_choice
                ai_piece = board.squares[ai_row][ai_col].piece

                if ai_piece:
                    ai_piece.clear_moves()
                    board.moves_calc(ai_piece, ai_row, ai_col, bool= True)

                    if board.valid_move(ai_piece, ai_move):
                        captured = board.squares[ai_move.final.row][ai_move.final.col].has_piece()
                        board.move(ai_piece, ai_move)
                        board.set_true_en_passant(ai_piece, ai_move)
                        game.play_sound(captured)
                        # AI always promotes to Queen
                        if board.promotion_pending:
                            from piece import Queen
                            board.apply_promotion(Queen)
                        game.next_turn()
                        # Check for checkmate
                        game.check_game_over()
            self.pending_ai = False

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
            # continue-> return because no longer in while loop
            return   # skip normal event handling while overlay is visible

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

                        # promotion picker
                        if board.promotion_pending:
                            self._resolve_promotion(screen, game, board)

                        # next turn
                        game.next_turn()
                        # check for checkmate
                        game.check_game_over()

                        if self.ai and game.next_player == self.ai.color: 
                                self.pending_ai = True

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

    def _resolve_promotion(self, screen, game, board):
        """Blocking loop: shows the picker until the player clicks a piece."""
        clock = pygame.time.Clock()
        while board.promotion_pending:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_pieces(screen)
            rects = game.show_promotion_menu(screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for cls, rect in rects.items():
                        if rect.collidepoint(event.pos):
                            board.apply_promotion(cls)
                            break
            clock.tick(60)

    # Addition of the menu screen
    def show_menu(self):
        screen = self.screen
        screen.fill((30, 30, 30))

        font = pygame.font.SysFont(None, 60)
        title_font = pygame.font.SysFont(None, 80)

        mouse_pos = pygame.mouse.get_pos()

        # Title
        title = title_font.render("Chess", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        # Buttons
        pvp_rect = pygame.Rect(0, 0, 400, 60)
        pvp_rect.center = (WIDTH // 2, HEIGHT // 2)

        ai_rect = pygame.Rect(0, 0, 400, 60)
        ai_rect.center = (WIDTH // 2, HEIGHT // 2 + 100)

        # Hover effects
        pvp_hover = pvp_rect.collidepoint(mouse_pos)
        ai_hover = ai_rect.collidepoint(mouse_pos)

        pvp_bg = (70, 70, 70) if pvp_hover else (50, 50, 50)
        ai_bg = (70, 70, 70) if ai_hover else (50, 50, 50)

        pvp_color = (255, 255, 255) if pvp_hover else (200, 200, 200)
        ai_color = (255, 255, 255) if ai_hover else (200, 200, 200)

        ### Rendering
        # Buttons
        pygame.draw.rect(screen, pvp_bg, pvp_rect, border_radius=8)
        pygame.draw.rect(screen, ai_bg, ai_rect, border_radius=8)

        # Render text
        pvp_text = font.render("Player vs Player", True, pvp_color)
        ai_text = font.render("Player vs AI", True, ai_color)

        pvp_text_rect = pvp_text.get_rect(center=pvp_rect.center)
        ai_text_rect = ai_text.get_rect(center=ai_rect.center)

        # draw it to screen
        screen.blit(title, title_rect)
        screen.blit(pvp_text, pvp_text_rect)
        screen.blit(ai_text, ai_text_rect)

        # Event handling for buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_rect.collidepoint(event.pos):
                    self.pending_ai = False
                    self.jeu = Jeu()
                    self.ai = None
                    self.state = "game"

                elif ai_rect.collidepoint(event.pos):
                    self.pending_ai = False
                    self.jeu = Jeu()
                    self.ai = AIPlayer(color="black", depth=3)
                    self.state = "game"

        pygame.display.update()

main = Main()
main.mainloop()
