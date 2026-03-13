import pygame
import os

from sound import Sound
from theme import Theme
class Settings():
    def __init__(self):
        self.themes = []
        self.add_themes()
        self.idx = 0
        self.theme = self.themes[self.idx]
        self.font = pygame.font.SysFont('monospace',18,bold=True)
        self.move_sound = Sound(os.path.join('assets/sounds/move.wav'))
        self.capture_sound = Sound(os.path.join('assets/sounds/capture.wav'))

    def change_theme(self):
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = self.themes[self.idx]

    def add_themes(self):
        brown = Theme((235, 209, 166),(165, 117, 80),(245, 234, 100),(209, 185, 59),'#C86464','#C84646')
        green = Theme((234, 235, 200),(119, 154, 88),(244, 247, 116),(172, 195, 51),'#C86464','#C84646')
        #blue = Theme()
        #gray = Theme()

        self.themes =[brown,green] #blue,#gray]