#This is the game class ( game == jeu(french)) :)

import pygame
from pygame import surface

from board import Board
from dimensions import *
from drag import Drag
class Jeu:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_square = None
        self.board = Board()
        self.drag = Drag()

    #Board rendering methods
    def show_bg(self,surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = (245, 230, 200) #Light_Brown
                else :
                    color = (190, 145, 95) #Dark_Brown

                rect =(col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)




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
        if self.drag.dragging:
            piece = self.drag.piece

            # Iterate all valid moves
            for move in piece.moves:
                #color
                color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C86464'
                #rectangle
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        if self.board.last_move:
            first= self.board.last_move.first
            final= self.board.last_move.final

            for pos in[first, final]:
                # color
                color = (244, 247, 116) if (pos.row ) % 2 == 0 else (172, 195, 51)
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