#This is the game class ( game == jeu(french)) :)

import pygame
from pygame import surface


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

    #Board rendering methods
    def show_bg(self,surface):
        theme = self.settings.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark

                rect =(col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

                #Rows coordinates
                if col == 0:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.settings.font.render(str(ROWS-row), True, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    #blit
                    surface.blit(lbl,lbl_pos)
                #Col coordinates
                if row ==7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.settings.font.render(str(Square.get_alphacol(col)), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)



    def show_pieces(self,surface):
        for row in range(ROWS):
            for col in range(COLS):
                #which piece needs to be rendered?
                if self.board.squares [row][col].has_piece():
                    piece = self.board.squares [row][col].piece
                    # All pieces except the piece being dragged
                    if piece is not self.drag.piece:
                        piece.set_texture(size = 80)
                        img = pygame.image.load(piece.texture)
                        img_center =col * SQSIZE + SQSIZE //2, row * SQSIZE + SQSIZE //2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)


    def show_moves(self, surface):
        theme = self.settings.theme
        if self.drag.dragging:
            piece = self.drag.piece

            # Iterate all valid moves
            for move in piece.moves:
                #color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                #rectangle
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.settings.theme
        if self.board.last_move:
            first= self.board.last_move.first
            final= self.board.last_move.final

            for pos in[first, final]:
                # color
                color = theme.trace.light if (pos.row ) % 2 == 0 else theme.trace.dark
                #rectangle
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                #blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_square:
            # color
            color = (180, 180 , 180)
            # rectangle
            rect = (self.hovered_square.col * SQSIZE, self.hovered_square.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width = 3)

    # method for next player
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_square = self.board.squares[row][col]

    def change_theme(self):
        self.settings.change_theme()

    def play_sound(self, captured = False):
        if captured:
            self.settings.capture_sound.play()
        else:
            self.settings.move_sound.play()

    def restart(self):
        self.__init__()