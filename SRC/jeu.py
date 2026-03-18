#This is the game class ( game == jeu(french)) :)

import pygame
from pygame import surface

from square import Square
from settings import Settings
from board import Board
from dimensions import *
from drag import Drag
from square import Square


class Jeu:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_square = None
        self.board = Board()
        self.drag = Drag()
        self.settings = Settings()
        # Game over state: None, 'checkmate', or 'stalemate'
        self.game_over = None
        self.winner = None  # 'White' or 'Black' or None for stalemate

    # ── Board rendering methods ──────────────────────────────────────────────

    def show_bg(self, surface):
        theme = self.settings.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark

                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

                # Rows coordinates
                if col == 0:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.settings.font.render(str(ROWS - row), True, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    surface.blit(lbl, lbl_pos)
                # Col coordinates
                if row == 7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.settings.font.render(str(Square.get_alphacol(col)), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # which piece needs to be rendered?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    # All pieces except the piece being dragged
                    if piece is not self.drag.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.settings.theme
        if self.drag.dragging:
            piece = self.drag.piece
            # Iterate all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rectangle
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.settings.theme
        if self.board.last_move:
            first = self.board.last_move.first
            final = self.board.last_move.final

            for pos in [first, final]:
                # Bug fix: use both row and col for correct checkerboard color
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_square:
            color = (180, 180, 180)
            rect = (self.hovered_square.col * SQSIZE, self.hovered_square.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    # ── Game-over overlay ────────────────────────────────────────────────────

    def show_game_over(self, surface):
        """Draw the winner/stalemate banner and the Play Again / Close buttons.
        Returns the pygame.Rect for each button so main.py can hit-test them."""

        # ── semi-transparent dark backdrop ──────────────────────────────────
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # ── fonts ────────────────────────────────────────────────────────────
        font_big   = pygame.font.SysFont('monospace', 52, bold=True)
        font_sub   = pygame.font.SysFont('monospace', 28, bold=True)
        font_btn   = pygame.font.SysFont('monospace', 22, bold=True)

        # ── headline text ────────────────────────────────────────────────────
        if self.game_over == 'checkmate':
            headline = f'{self.winner} Wins!'
            sub_text = 'Checkmate'
            headline_color = (255, 215, 0)   # gold
        else:
            headline = "Stalemate!"
            sub_text = "It's a draw"
            headline_color = (200, 200, 200)

        h_surf = font_big.render(headline, True, headline_color)
        s_surf = font_sub.render(sub_text, True, (220, 220, 220))

        cx = WIDTH // 2
        cy = HEIGHT // 2

        # draw headline + subtext centred
        surface.blit(h_surf, h_surf.get_rect(center=(cx, cy - 90)))
        surface.blit(s_surf, s_surf.get_rect(center=(cx, cy - 30)))

        # ── prompt ───────────────────────────────────────────────────────────
        prompt_surf = font_sub.render('Wanna play again?', True, (255, 255, 255))
        surface.blit(prompt_surf, prompt_surf.get_rect(center=(cx, cy + 30)))

        # ── buttons ──────────────────────────────────────────────────────────
        btn_w, btn_h = 190, 52
        gap = 30

        restart_rect = pygame.Rect(cx - btn_w - gap // 2, cy + 80, btn_w, btn_h)
        close_rect   = pygame.Rect(cx + gap // 2,          cy + 80, btn_w, btn_h)

        # Restart button  (green-ish)
        pygame.draw.rect(surface, (46, 139, 87),  restart_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), restart_rect, 2, border_radius=10)
        r_lbl = font_btn.render('▶  Play Again', True, (255, 255, 255))
        surface.blit(r_lbl, r_lbl.get_rect(center=restart_rect.center))

        # Close button  (red-ish)
        pygame.draw.rect(surface, (178, 34, 34),  close_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), close_rect, 2, border_radius=10)
        c_lbl = font_btn.render('✕  Close', True, (255, 255, 255))
        surface.blit(c_lbl, c_lbl.get_rect(center=close_rect.center))

        return restart_rect, close_rect

    # ── Post-move game-state check ───────────────────────────────────────────

    def check_game_over(self):
        """Call after every move to detect checkmate or stalemate for the
        player who now has to move (self.next_player)."""
        color = self.next_player
        if self.board.is_checkmate(color):
            self.game_over = 'checkmate'
            # The winner is the OTHER player (the one who just moved)
            self.winner = 'White' if color == 'black' else 'Black'
        elif self.board.is_stalemate(color):
            self.game_over = 'stalemate'
            self.winner = None

        # Clean up any stale move lists left on pieces from the detection scan
        for row in range(ROWS):
            for col in range(COLS):
                sq = self.board.squares[row][col]
                if sq.has_piece():
                    sq.piece.clear_moves()

    # ── Utility methods ──────────────────────────────────────────────────────

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        # clamp to valid board range
        row = max(0, min(row, ROWS - 1))
        col = max(0, min(col, COLS - 1))
        self.hovered_square = self.board.squares[row][col]

    def change_theme(self):
        self.settings.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.settings.capture_sound.play()
        else:
            self.settings.move_sound.play()

    def restart(self):
        self.__init__()
