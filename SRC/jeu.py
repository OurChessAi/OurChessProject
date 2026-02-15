#This is the game class ( game == jeu(french)) :)

import pygame


from board import Board
from dimensions import *
class Jeu:

    def __init__(self):
        self.board = Board()

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

                    img = pygame.image.load(piece.texture)
                    img_center =col * SQSIZE + SQSIZE //2, row * SQSIZE + SQSIZE //2
                    piece.texture_rect = img.get_rect(center = img_center)
                    surface.blit(img, piece.texture_rect)
